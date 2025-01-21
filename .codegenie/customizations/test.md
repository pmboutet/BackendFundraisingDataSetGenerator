# Testing Practices Cheat Sheet

## Testing Libraries and Frameworks

- Jest: Primary testing framework in use
- React Testing Library: For testing React components
- Enzyme: For additional React component testing capabilities
- Sinon: For creating spies, stubs, and mocks

## Mocking and Stubbing

### Jest Mocks

```javascript
jest.mock('./someModule');
jest.spyOn(object, 'method').mockImplementation(() => mockReturnValue);
```

### Sinon Stubs

```javascript
const stub = sinon.stub(object, 'method').returns(mockValue);
```

## Fake Implementations

### In-Memory Database

```javascript
const fakeDatabase = {
  users: [],
  addUser: (user) => fakeDatabase.users.push(user),
  getUser: (id) => fakeDatabase.users.find(user => user.id === id)
};
```

### Mock API Responses

```javascript
const mockApiResponse = {
  data: { /* mock data structure */ },
  status: 200
};
```

## Asynchronous Testing

### Async/Await

```javascript
test('async operation', async () => {
  const result = await someAsyncFunction();
  expect(result).toBe(expectedValue);
});
```

### Promises

```javascript
test('promise-based operation', () => {
  return somePromiseFunction().then(result => {
    expect(result).toBe(expectedValue);
  });
});
```

## Component Testing

### Snapshot Testing

```javascript
it('renders correctly', () => {
  const tree = renderer.create(<MyComponent />).toJSON();
  expect(tree).toMatchSnapshot();
});
```

### Event Simulation

```javascript
test('handles click event', () => {
  const { getByText } = render(<MyComponent />);
  fireEvent.click(getByText('Click me'));
  expect(/* assertion */);
});
```

## Test Organization

- Describe blocks for grouping related tests
- BeforeEach/AfterEach for setup and teardown
- Use of factory functions for creating test data

## Code Coverage

- Jest's built-in coverage reporting
- Aim for high coverage, especially in critical paths

## Best Practices

- One assertion per test when possible
- Use descriptive test names
- Avoid testing implementation details
- Use data-testid attributes for component querying

## Error Handling

- Test both success and error scenarios
- Use try-catch blocks in async tests when necessary

## Environment Variables

- Use .env.test for test-specific environment variables

## Continuous Integration

- Tests run on every pull request
- All tests must pass before merging