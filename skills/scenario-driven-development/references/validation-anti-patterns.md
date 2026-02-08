# Testing Anti-Patterns

## Overview

Test what the code does, not what the mocks do.

Every anti-pattern here leads to the same failure: tests pass, code is broken. The test suite becomes a false comfort blanket that hides bugs instead of catching them.

## The Iron Laws

```
1. NEVER test mock behavior — test real behavior through mocks
2. NEVER add methods to production code that exist only for tests
3. NEVER mock what you don't understand
```

## Anti-Pattern 1: Testing Mock Behavior

### Violation

```python
def test_user_service():
    db = Mock()
    db.find.return_value = {"name": "Alice"}
    service = UserService(db)
    result = service.get_user(1)
    assert result == {"name": "Alice"}  # Testing that the mock returns what you told it to
```

### Why It's Wrong

You told the mock to return `{"name": "Alice"}`. Then you verified it returned `{"name": "Alice"}`. You tested the mock framework, not your code. If `UserService.get_user` has a bug in how it processes the database result, this test still passes.

### Fix

```python
def test_user_service_formats_display_name():
    db = Mock()
    db.find.return_value = {"first": "Alice", "last": "Smith"}
    service = UserService(db)
    result = service.get_user(1)
    assert result.display_name == "Alice Smith"  # Testing YOUR code's transformation
```

### Gate Function

```
□ Does the assertion test something YOUR code computes?
□ If you change the mock return value, does the expected assertion also change?
□ Would a bug in your code cause this test to fail?
```

If any answer is "no," you're testing mock behavior.

## Anti-Pattern 2: Test-Only Methods in Production

### Violation

```python
class PaymentProcessor:
    def process(self, amount):
        self._validate(amount)
        self._charge(amount)
        self._notify()

    def _get_internal_state(self):  # Added just for tests
        return self._state

    def _set_test_mode(self, mode):  # Added just for tests
        self._test_mode = mode
```

### Why It's Wrong

Production code should not know about tests. Test-only methods increase the API surface, create maintenance burden, and signal that the design is wrong. If you can't test through public interfaces, your design needs to change.

### Fix

```python
# Test through public interface
def test_process_valid_amount():
    processor = PaymentProcessor(gateway=mock_gateway)
    processor.process(50.00)
    mock_gateway.charge.assert_called_once_with(50.00)

# Or extract the internal logic into a testable unit
class AmountValidator:
    def validate(self, amount):
        if amount <= 0:
            raise InvalidAmount(amount)
```

### Gate Function

```
□ Does every method in production code serve a production purpose?
□ Can all behavior be tested through public interfaces?
□ Would removing this method break production functionality?
```

If a method exists only for tests, delete it and redesign.

## Anti-Pattern 3: Mocking Without Understanding

### Violation

```python
def test_complex_workflow():
    service_a = Mock()
    service_b = Mock()
    service_c = Mock()
    # 20 lines of mock setup you copied from somewhere
    service_a.process.return_value = Mock(status="ok", data=Mock(items=[]))
    service_b.transform.side_effect = lambda x: x
    # ... you don't know what these do, but the test passes
```

### Why It's Wrong

If you don't understand why the mock returns what it returns, you don't understand what you're testing. The mock setup encodes assumptions about collaborator behavior. Wrong assumptions = useless test.

### Fix

```python
# Understand each collaborator's contract
# service_a.process returns ProcessResult with status and items
# service_b.transform maps items to output format

def test_workflow_transforms_processed_items():
    processed = ProcessResult(status="ok", items=[Item("x")])
    service_a = Mock()
    service_a.process.return_value = processed

    workflow = Workflow(service_a, real_transformer)
    result = workflow.run()

    assert result.items == [TransformedItem("x")]
```

### Gate Function

```
□ Can you explain what each mock return value represents?
□ Can you explain why each side_effect behaves as configured?
□ Do mock return types match real return types?
```

If you can't explain the mocks, you can't trust the test.

## Anti-Pattern 4: Incomplete Mocks

### Violation

```python
def test_api_call():
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
def test_api_call():
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
□ Does mock match the real dependency's interface? (use spec= when available)
□ Does mock return the same TYPE as the real dependency?
□ Are error cases mocked with realistic error types?
```

If the mock's shape differs from reality, the test is a lie.

## Anti-Pattern 5: Integration Tests as Afterthought

### Violation

```
test/
├── unit/          # 200 tests, all mocked
└── integration/   # 2 tests, added before release
```

### Why It's Wrong

Unit tests with mocks verify your code works with your assumptions. Integration tests verify your assumptions are correct. Without integration tests, every mock return value is an unverified assumption.

### Fix

Plan integration tests during design, not after:

```
test/
├── unit/          # Fast, mocked, high coverage of logic
├── integration/   # Verifies assumptions at boundaries
└── e2e/           # Verifies complete workflows
```

**Rule of thumb:** For every mock you create, ask: "Where is the test that proves this mock behaves like the real thing?"

## Structural Anti-Patterns

### Ice Cream Cone

**Symptom:** More E2E tests than unit tests. Test suite is slow, flaky, and expensive to maintain.

**Fix:** Invert the pyramid. Most tests should be fast unit tests. Integration tests at boundaries. E2E tests for critical paths only.

### Giant Test

**Symptom:** Single test with 100+ lines, multiple assertions, complex setup.

**Fix:** Split into focused tests. Each test verifies one behavior. Share setup through fixtures/factories, not copy-paste.

### Fragile Test

**Symptom:** Tests break when implementation changes but behavior stays the same.

**Fix:** Test behavior, not implementation. Assert on outputs, not on internal method calls. Use `assert result == expected`, not `mock.method.assert_called_with(internal_detail)`.

### Shared State

**Symptom:** Tests pass individually, fail together. Test order matters.

**Fix:** Each test creates its own state. Use setup/teardown to ensure clean state. Never rely on side effects from other tests.

## Process Anti-Patterns

### Code-First Testing

**Symptom:** Write all production code, then write tests to cover it.

**Problem:** Tests confirm what you built, not what you should have built. Edge cases are missed because you test what you see, not what could happen.

**Fix:** Follow TDD. RED → GREEN → REFACTOR. Every time.

### Safety Net Illusion

**Symptom:** High code coverage, but tests don't catch real bugs.

**Problem:** Coverage measures lines executed, not correctness verified. `assert true` covers a line but tests nothing.

**Fix:** Review assertions, not coverage. Every test should have a meaningful assertion that would fail if the code were wrong.

### Spike That Stayed

**Symptom:** Prototype code went to production without being rewritten with tests.

**Problem:** Spike code has no tests, no edge case handling, no error handling. It was meant to be thrown away.

**Fix:** Delete the spike. Rebuild with TDD. The spike taught you the shape; TDD builds it correctly.

## When Mocks Become Too Complex

**Warning signs:**
- Mock setup is longer than the test
- You need mocks that return mocks
- You're mocking more than 3 dependencies
- Mock behavior is hard to explain

**Alternatives:**
- **Fakes:** In-memory implementations that behave like real dependencies (in-memory database, fake HTTP server)
- **Extract and test:** Pull logic out of the heavily-dependent class into a pure function
- **Integration test:** If mocking is too complex, test with the real dependency
- **Redesign:** Complex mocking often signals complex coupling — simplify the architecture

## Quick Reference

| Anti-Pattern | Fix |
|-------------|-----|
| Testing mock return values | Assert on YOUR code's transformation |
| Test-only production methods | Test through public interface or extract |
| Copy-pasted mock setup | Understand each mock's purpose |
| Mock returns wrong type | Use spec= or match real interface |
| No integration tests | Test assumptions at boundaries |
| Ice cream cone | Invert to testing pyramid |
| Giant tests | Split into focused behaviors |
| Fragile tests | Assert behavior, not implementation |
| Shared test state | Isolate each test completely |
| Code-first testing | TDD: RED → GREEN → REFACTOR |

## Red Flags

You're in an anti-pattern if:
- Tests pass but production breaks
- Changing implementation breaks tests that should still pass
- You can't explain what a test verifies without reading the mock setup
- Test suite takes minutes to run for a small codebase
- You're afraid to refactor because tests might break
- Adding a feature requires changing 20 existing tests
- Coverage is high but confidence is low
