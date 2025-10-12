#!/usr/bin/env python3
"""
Claude Code Notify
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
from datetime import datetime


class ClaudePromptTracker:
    def __init__(self):
        """Initialize the prompt tracker with database setup"""
        # Use current working directory (user's project) for database and logs
        self.project_root = self.find_project_root()
        self.db_path = os.path.join(self.project_root, ".claude", "ccnotify.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.setup_logging()
        self.init_database()

    def find_project_root(self):
        """Find project root using current working directory (where Claude Code was started)"""
        current = os.getcwd()
        max_levels = 20  # Prevent infinite loops

        # Check if current directory has .claude
        if os.path.exists(os.path.join(current, ".claude")) and os.path.isdir(
            os.path.join(current, ".claude")
        ):
            return current

        # Search upward for directory that CONTAINS .claude
        for _ in range(max_levels):
            parent = os.path.dirname(current)
            if parent == current:  # Reached root
                break
            if os.path.exists(os.path.join(current, ".claude")) and os.path.isdir(
                os.path.join(current, ".claude")
            ):
                return current
            current = parent

        # Fallback to cwd if not found
        return os.getcwd()

    def setup_logging(self):
        """Setup logging to daily logs directory in user's project"""
        from datetime import datetime

        # Create logs dir for today in user's project
        today = datetime.now().strftime("%Y-%m-%d")
        logs_dir = os.path.join(self.project_root, ".claude", "logs", today)
        os.makedirs(logs_dir, exist_ok=True)

        log_path = os.path.join(logs_dir, "ccnotify.log")

        # Create a simple file handler (no rotation needed, new file each day)
        handler = logging.FileHandler(
            log_path, mode="a", encoding="utf-8"  # Append mode
        )

        # Set the log format
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Configure the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def init_database(self):
        """Create tables and triggers if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            # Create main table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    prompt TEXT,
                    cwd TEXT,
                    seq INTEGER,
                    stoped_at DATETIME,
                    lastWaitUserAt DATETIME
                )
            """
            )

            # Create trigger for auto-incrementing seq
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS auto_increment_seq
                AFTER INSERT ON prompt
                FOR EACH ROW
                BEGIN
                    UPDATE prompt 
                    SET seq = (
                        SELECT COALESCE(MAX(seq), 0) + 1 
                        FROM prompt 
                        WHERE session_id = NEW.session_id
                    )
                    WHERE id = NEW.id;
                END
            """
            )

            conn.commit()

    def handle_user_prompt_submit(self, data):
        """Handle UserPromptSubmit event - insert new prompt record"""
        session_id = data.get("session_id")
        prompt = data.get("prompt", "")
        cwd = data.get("cwd", "")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO prompt (session_id, prompt, cwd)
                VALUES (?, ?, ?)
            """,
                (session_id, prompt, cwd),
            )
            conn.commit()

        logging.info(f"Recorded prompt for session {session_id}")

    def handle_stop(self, data):
        """Handle Stop event - update completion time and send notification"""
        session_id = data.get("session_id")

        with sqlite3.connect(self.db_path) as conn:
            # Find the latest unfinished record for this session
            cursor = conn.execute(
                """
                SELECT id, created_at, cwd
                FROM prompt 
                WHERE session_id = ? AND stoped_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if row:
                record_id, created_at, cwd = row

                # Update completion time
                conn.execute(
                    """
                    UPDATE prompt 
                    SET stoped_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (record_id,),
                )
                conn.commit()

                # Get seq number and calculate duration
                cursor = conn.execute(
                    "SELECT seq FROM prompt WHERE id = ?", (record_id,)
                )
                seq_row = cursor.fetchone()
                seq = seq_row[0] if seq_row else 1

                duration = self.calculate_duration_from_db(record_id)
                self.send_notification(
                    title=os.path.basename(cwd) if cwd else "Claude Task",
                    subtitle=f"job#{seq} done, duration: {duration}",
                    cwd=cwd,
                )

                logging.info(
                    f"Task completed for session {session_id}, job#{seq}, duration: {duration}"
                )

    def handle_notification(self, data):
        """Handle Notification event - check for waiting input and send notification"""
        session_id = data.get("session_id")
        message = data.get("message", "")

        # Comprehensive patterns for all blocking situations requiring user action
        blocked_patterns = [
            # Direct input requests
            "waiting for your input",
            "please provide",
            "need your input",
            "enter your",
            "type your",
            # Permission and authorization
            "requires authorization",
            "permission required",
            "needs your permission",  # ✅ PATRÓN CRÍTICO AÑADIDO
            "needs permission",
            "tool requires approval",
            "requires confirmation",
            "waiting for approval",
            "permission to use",  # ✅ PATRÓN ADICIONAL
            "grant permission",
            "allow access",
            "authorize this",
            # Blocking situations
            "blocked by",
            "access denied",
            "cannot proceed",
            "unable to continue",
            "stopped waiting",
            "requires user confirmation",
            # Claude Code specific messages
            "ask the user",
            "user approval",
            "confirm this action",
            "do you want to",
            "should i proceed",
            "proceed with",
            "continue with",
            # Tool-specific blocks
            "bash tool",
            "file operation",
            "potentially dangerous",
            "security check",
            "verify this",
        ]

        message_lower = message.lower()
        if any(pattern in message_lower for pattern in blocked_patterns):
            cwd = data.get("cwd", "")

            with sqlite3.connect(self.db_path) as conn:
                # Update lastWaitUserAt for the latest record
                conn.execute(
                    """
                    UPDATE prompt 
                    SET lastWaitUserAt = CURRENT_TIMESTAMP
                    WHERE id = (
                        SELECT id FROM prompt 
                        WHERE session_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    )
                """,
                    (session_id,),
                )
                conn.commit()

            # Enhanced notification subtitle with more specific categorization
            if any(
                wait in message_lower
                for wait in [
                    "waiting for your input",
                    "need your input",
                    "please provide",
                ]
            ):
                subtitle = "🔴 Waiting for input"
            elif any(
                perm in message_lower
                for perm in [
                    "permission",
                    "authorization",
                    "approval",
                    "confirm",
                    "allow",
                ]
            ):
                subtitle = "🔒 Permission required"
            elif any(
                block in message_lower
                for block in ["blocked by", "access denied", "cannot proceed"]
            ):
                subtitle = "⚠️ Action blocked"
            elif any(
                tool in message_lower
                for tool in ["bash tool", "file operation", "dangerous"]
            ):
                subtitle = "🛠️ Tool approval needed"
            else:
                subtitle = "❗ Action needed"

            self.send_notification(
                title=os.path.basename(cwd) if cwd else "Claude Task",
                subtitle=subtitle,
                cwd=cwd,
            )

            logging.info(
                f"Block notification sent for session {session_id}: {subtitle}"
            )

    def calculate_duration_from_db(self, record_id):
        """Calculate duration for a completed record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT created_at, stoped_at
                FROM prompt
                WHERE id = ?
            """,
                (record_id,),
            )

            row = cursor.fetchone()
            if row and row[1]:
                return self.calculate_duration(row[0], row[1])

        return "Unknown"

    def calculate_duration(self, start_time, end_time):
        """Calculate human-readable duration between two timestamps"""
        try:
            if isinstance(start_time, str):
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            else:
                start_dt = datetime.fromisoformat(start_time)

            if isinstance(end_time, str):
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            else:
                end_dt = datetime.fromisoformat(end_time)

            duration = end_dt - start_dt
            total_seconds = int(duration.total_seconds())

            if total_seconds < 60:
                return f"{total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                if seconds > 0:
                    return f"{minutes}m{seconds}s"
                else:
                    return f"{minutes}m"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                if minutes > 0:
                    return f"{hours}h{minutes}m"
                else:
                    return f"{hours}h"
        except Exception as e:
            logging.error(f"Error calculating duration: {e}")
            return "Unknown"

    def send_notification(self, title, subtitle, cwd=None):
        """Send macOS notification using terminal-notifier"""
        from datetime import datetime

        current_time = datetime.now().strftime("%B %d, %Y at %H:%M")

        try:
            # Enhanced notification with critical priority and persistent alert
            cmd = [
                "terminal-notifier",
                "-sound",
                "Sosumi",  # More noticeable sound
                "-title",
                title,
                "-subtitle",
                f"{subtitle}\n{current_time}",
                "-timeout",
                "30",  # Stay visible longer
                "-sender",
                "com.apple.Terminal",  # Ensure proper app identification
            ]

            # For permission/approval notifications, make them more persistent
            if (
                "permission" in subtitle.lower()
                or "approval" in subtitle.lower()
                or "waiting" in subtitle.lower()
            ):
                cmd.extend(
                    [
                        "-ignoreDnD",  # Ignore Do Not Disturb
                        "-sticky",  # Stay until dismissed
                    ]
                )

            if cwd:
                cmd.extend(["-execute", f'/usr/local/bin/code "{cwd}"'])

            subprocess.run(cmd, check=False, capture_output=True)
            logging.info(f"Enhanced notification sent: {title} - {subtitle}")
        except FileNotFoundError:
            logging.warning("terminal-notifier not found, notification skipped")
        except Exception as e:
            logging.error(f"Error sending notification: {e}")


def validate_input_data(data, expected_event_name):
    """Validate input data matches design specification"""
    required_fields = {
        "UserPromptSubmit": ["session_id", "prompt", "cwd", "hook_event_name"],
        "Stop": ["session_id", "hook_event_name"],
        "Notification": [
            "session_id",
            "message",
            "hook_event_name",
            "transcript_path",
            "cwd",
        ],
    }

    if expected_event_name not in required_fields:
        raise ValueError(f"Unknown event type: {expected_event_name}")

    # Check hook_event_name matches expected
    if data.get("hook_event_name") != expected_event_name:
        raise ValueError(
            f"Event name mismatch: expected {expected_event_name}, got {data.get('hook_event_name')}"
        )

    # Check core required fields (some fields may be optional depending on context)
    core_fields = {
        "UserPromptSubmit": ["session_id", "hook_event_name"],
        "Stop": ["session_id", "hook_event_name"],
        "Notification": [
            "session_id",
            "hook_event_name",
        ],  # message might be empty, paths optional
    }

    missing_fields = []
    for field in core_fields[expected_event_name]:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(
            f"Missing core required fields for {expected_event_name}: {missing_fields}"
        )

    return True


def main():
    """Main entry point - read JSON from stdin and process event"""
    try:
        # Check if hook type is provided as command line argument
        if len(sys.argv) < 2:
            print("ok")
            return

        expected_event_name = sys.argv[1]
        valid_events = ["UserPromptSubmit", "Stop", "Notification"]

        if expected_event_name not in valid_events:
            logging.error(f"Invalid hook type: {expected_event_name}")
            logging.error(f"Valid hook types: {', '.join(valid_events)}")
            sys.exit(1)

        # Read JSON data from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            logging.warning("No input data received")
            return

        data = json.loads(input_data)

        # Validate input data
        validate_input_data(data, expected_event_name)

        tracker = ClaudePromptTracker()

        if expected_event_name == "UserPromptSubmit":
            tracker.handle_user_prompt_submit(data)
        elif expected_event_name == "Stop":
            tracker.handle_stop(data)
        elif expected_event_name == "Notification":
            tracker.handle_notification(data)

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
