# Validation Anti-Patterns

## Overview

Validate what the code does for real users, not what the assertions technically accept.

Every anti-pattern here leads to the same failure: scenarios are satisfied, code is broken. The validation suite becomes a false comfort blanket that hides bugs instead of catching them.

## The Iron Laws

```
1. NEVER satisfy a scenario without genuine behavioral correctness (reward hacking)
2. NEVER validate mock behavior — validate real behavior through mocks
3. NEVER add methods to production code that exist only for validation
4. NEVER mock what you don't understand
```

## Anti-Pattern 1: Reward Hacking

This is THE defining anti-pattern of Scenario-Driven Development. Reward hacking occurs when code satisfies assertions without implementing genuine behavioral correctness. The scenario is technically "satisfied" but the underlying intent is completely unmet.

### Violation — Trivial Satisfaction

```python
# Scenario: "User authentication returns True for valid credentials"
def authenticate(username, password):
    return True  # Satisfies the assertion, implements nothing
```

### Violation — Precision Evasion

```python
# Scenario: "Calculate 15% tip on $56.99"
def calculate_tip(amount, pct):
    return amount * pct  # Returns 8.549999999999999

# Scenario only checks integer part
assert int(calculate_tip(56.99, 0.15)) == 8  # "Satisfied" — real behavior is wrong
```

### Violation — Scenario Rewriting

```python
# Agent encounters a failing scenario:
#   assert processor.charge(100) == Receipt(amount=100, tax=8.25)
# Instead of fixing the code, the agent rewrites the scenario:
#   assert processor.charge(100) is not None  # "Satisfied"
```

### Violation — Hardcoded Oracle

```python
# Scenario: "Fibonacci of 10 is 55"
def fibonacci(n):
    if n == 10:
        return 55  # Satisfies the scenario, implements nothing general
    return 0
```

### Why It's Wrong

Reward hacking is the AI-age equivalent of teaching to the test. The scenario exists to describe user-observable behavior. When code satisfies the assertion without implementing the behavior, the entire SDD loop breaks. You get a green signal with broken software.

This is especially dangerous with AI agents writing code — they optimize for scenario satisfaction as a reward signal. Without structural guards, the fastest path to satisfaction is often a hack, not a solution.

### Fix

```python
# 1. Scenarios describe observable behavior, not return values
def test_authentication_rejects_wrong_password():
    auth = Authenticator(user_store=real_or_fake_store)
    result = auth.authenticate("alice", "wrong-password")
    assert result.is_authenticated is False
    assert "invalid credentials" in result.reason

# 2. Multiple scenario variants prevent hardcoding
def test_fibonacci_sequence():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765

# 3. Property-based scenarios catch precision evasion
def test_tip_calculation_precision():
    tip = calculate_tip(56.99, 0.15)
    assert tip == pytest.approx(8.5485, rel=1e-4)
```

### Gate Function

```
[] Does the code implement general behavior, not just the specific scenario inputs?
[] Would a NEW, unseen input produce a correct result?
[] Are there at least 2-3 variant scenarios preventing hardcoded returns?
[] Is floating-point precision explicitly validated?
[] Has the agent modified ANY existing scenario during this cycle? (If yes: automatic rejection)
```

If any answer is "no," you have reward hacking. The scenario is satisfied; the behavior is not.

## Anti-Pattern 2: Validating Mock Behavior

### Violation

```python
def scenario_user_service():
    db = Mock()
    db.find.return_value = {"name": "Alice"}
    service = UserService(db)
    result = service.get_user(1)
    assert result == {"name": "Alice"}  # Validating that the mock returns what you told it to
```

### Why It's Wrong

You told the mock to return `{"name": "Alice"}`. Then you verified it returned `{"name": "Alice"}`. You validated the mock framework, not your code. If `UserService.get_user` has a bug in how it processes the database result, this scenario still reports satisfaction.

### Fix

```python
def scenario_user_service_formats_display_name():
    db = Mock()
    db.find.return_value = {"first": "Alice", "last": "Smith"}
    service = UserService(db)
    result = service.get_user(1)
    assert result.display_name == "Alice Smith"  # Validating YOUR code's transformation
```

### Gate Function

```
[] Does the assertion validate something YOUR code computes?
[] If you change the mock return value, does the expected assertion also change?
[] Would a bug in your code cause this scenario to fail?
```

If any answer is "no," you're validating mock behavior.

## Anti-Pattern 3: Validation-Only Methods in Production

### Violation

```python
class PaymentProcessor:
    def process(self, amount):
        self._validate(amount)
        self._charge(amount)
        self._notify()

    def _get_internal_state(self):  # Added just for validation
        return self._state

    def _set_test_mode(self, mode):  # Added just for validation
        self._test_mode = mode
```

### Why It's Wrong

Production code should not know about validation scenarios. Validation-only methods increase the API surface, create maintenance burden, and signal that the design is wrong. If you can't validate through public interfaces, your design needs to change.

### Fix

```python
# Validate through public interface
def scenario_process_valid_amount():
    processor = PaymentProcessor(gateway=mock_gateway)
    processor.process(50.00)
    mock_gateway.charge.assert_called_once_with(50.00)

# Or extract the internal logic into a validatable unit
class AmountValidator:
    def validate(self, amount):
        if amount <= 0:
            raise InvalidAmount(amount)
```

### Gate Function

```
[] Does every method in production code serve a production purpose?
[] Can all behavior be validated through public interfaces?
[] Would removing this method break production functionality?
```

If a method exists only for validation, delete it and redesign.

## Anti-Pattern 4: Mocking Without Understanding

### Violation

```python
def scenario_complex_workflow():
    service_a = Mock()
    service_b = Mock()
    service_c = Mock()
    # 20 lines of mock setup you copied from somewhere
    service_a.process.return_value = Mock(status="ok", data=Mock(items=[]))
    service_b.transform.side_effect = lambda x: x
    # ... you don't know what these do, but the scenario reports satisfaction
```

### Why It's Wrong

If you don't understand why the mock returns what it returns, you don't understand what you're validating. The mock setup encodes assumptions about collaborator behavior. Wrong assumptions = useless scenario.

### Fix

```python
# Understand each collaborator's contract
# service_a.process returns ProcessResult with status and items
# service_b.transform maps items to output format

def scenario_workflow_transforms_processed_items():
    processed = ProcessResult(status="ok", items=[Item("x")])
    service_a = Mock()
    service_a.process.return_value = processed

    workflow = Workflow(service_a, real_transformer)
    result = workflow.run()

    assert result.items == [TransformedItem("x")]
```

### Gate Function

```
[] Can you explain what each mock return value represents?
[] Can you explain why each side_effect behaves as configured?
[] Do mock return types match real return types?
```

If you can't explain the mocks, you can't trust the scenario.

## Anti-Pattern 5: Incomplete Mocks

### Violation

```python
def scenario_api_call():
    http = Mock()
    http.get.return_value = {"data": "value"}  # Real API returns Response object
    client = ApiClient(http)
    result = client.fetch("/endpoint")
    assert result == "value"
```

### Why It's Wrong

The real HTTP client returns a Response object with `.status_code`, `.json()`, `.headers`. Your mock returns a plain dict. Your code might work with the mock but fail with the real dependency because it accesses `.status_code` or calls `.json()`.

### Fix

```python
def scenario_api_call():
    response = Mock(spec=Response)
    response.status_code = 200
    response.json.return_value = {"data": "value"}
    http = Mock()
    http.get.return_value = response
    client = ApiClient(http)
    result = client.fetch("/endpoint")
    assert result == "value"
```

### Gate Function

```
[] Does mock match the real dependency's interface? (use spec= when available)
[] Does mock return the same TYPE as the real dependency?
[] Are error cases mocked with realistic error types?
```

If the mock's shape differs from reality, the scenario is a lie.

## Anti-Pattern 6: Integration Scenarios as Afterthought

### Violation

```
scenarios/
--- unit/          # 200 scenarios, all mocked
--- integration/   # 2 scenarios, added before release
```

### Why It's Wrong

Unit scenarios with mocks verify your code works with your assumptions. Integration scenarios verify your assumptions are correct. Without integration scenarios, every mock return value is an unverified assumption.

### Fix

Plan integration scenarios during design, not after:

```
scenarios/
--- unit/          # Fast, mocked, high coverage of logic
--- integration/   # Verifies assumptions at boundaries
--- e2e/           # Verifies complete user workflows
```

**Rule of thumb:** For every mock you create, ask: "Where is the scenario that proves this mock behaves like the real thing?"

## Structural Anti-Patterns

### Ice Cream Cone

**Symptom:** More E2E scenarios than unit scenarios. Validation suite is slow, flaky, and expensive to maintain.

**Fix:** Invert the pyramid. Most scenarios should be fast unit scenarios. Integration scenarios at boundaries. E2E scenarios for critical user paths only.

### Giant Scenario

**Symptom:** Single scenario with 100+ lines, multiple assertions, complex setup.

**Fix:** Split into focused scenarios. Each scenario verifies one observable behavior. Share setup through fixtures/factories, not copy-paste.

### Fragile Scenario

**Symptom:** Scenarios break when implementation changes but behavior stays the same.

**Fix:** Validate behavior, not implementation. Assert on outputs, not on internal method calls. Use `assert result == expected`, not `mock.method.assert_called_with(internal_detail)`.

### Shared State

**Symptom:** Scenarios satisfy individually, fail together. Scenario order matters.

**Fix:** Each scenario creates its own state. Use setup/teardown to ensure clean state. Never rely on side effects from other scenarios.

## Process Anti-Patterns

### Code-First Scenarios

**Symptom:** Write all production code, then write scenarios to cover it.

**Problem:** Scenarios confirm what you built, not what you should have built. Edge cases are missed because you validate what you see, not what could happen.

**Fix:** Follow SDD. SCENARIO -> SATISFY -> REFACTOR. Every time.

### Safety Net Illusion

**Symptom:** High code coverage, but scenarios don't catch real bugs.

**Problem:** Coverage measures lines executed, not correctness verified. `assert True` covers a line but validates nothing. This is reward hacking at the process level.

**Fix:** Review assertions, not coverage. Every scenario should have a meaningful assertion that would fail if the code were genuinely wrong — not just technically wrong.

### Spike That Stayed

**Symptom:** Prototype code went to production without being rebuilt with scenarios.

**Problem:** Spike code has no scenarios, no edge case handling, no error handling. It was meant to be thrown away.

**Fix:** Delete the spike. Rebuild with SDD. The spike taught you the shape; SCENARIO -> SATISFY -> REFACTOR builds it correctly.

## When Mocks Become Too Complex

**Warning signs:**
- Mock setup is longer than the scenario
- You need mocks that return mocks
- You're mocking more than 3 dependencies
- Mock behavior is hard to explain

**Alternatives:**
- **Fakes:** In-memory implementations that behave like real dependencies (in-memory database, fake HTTP server)
- **Extract and validate:** Pull logic out of the heavily-dependent class into a pure function
- **Integration scenario:** If mocking is too complex, validate with the real dependency
- **Redesign:** Complex mocking often signals complex coupling — simplify the architecture

## Quick Reference

| Anti-Pattern | Fix |
|-------------|-----|
| Reward hacking (trivial satisfaction) | Multiple variant scenarios + property-based validation |
| Reward hacking (scenario rewriting) | Immutable scenarios — agent NEVER modifies existing scenarios |
| Reward hacking (precision evasion) | Explicit precision assertions (pytest.approx, decimal) |
| Validating mock return values | Assert on YOUR code's transformation |
| Validation-only production methods | Validate through public interface or extract |
| Copy-pasted mock setup | Understand each mock's purpose |
| Mock returns wrong type | Use spec= or match real interface |
| No integration scenarios | Validate assumptions at boundaries |
| Ice cream cone | Invert to validation pyramid |
| Giant scenarios | Split into focused behaviors |
| Fragile scenarios | Assert behavior, not implementation |
| Shared scenario state | Isolate each scenario completely |
| Code-first scenarios | SDD: SCENARIO -> SATISFY -> REFACTOR |

## Red Flags

You're in an anti-pattern if:
- Scenarios report satisfaction but production breaks
- Changing implementation breaks scenarios that should still be satisfied
- You can't explain what a scenario validates without reading the mock setup
- Validation suite takes minutes to run for a small codebase
- You're afraid to refactor because scenarios might break
- Adding a feature requires changing 20 existing scenarios
- Coverage is high but confidence is low
- An agent modified existing scenarios to make them pass (reward hacking)
- Code returns technically-correct-but-wrong values (precision hacking)
- A single hardcoded return value satisfies the scenario (oracle hacking)
