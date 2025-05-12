# Utilities API Reference

Neo4j-ORM provides several utility classes and functions to help with common tasks. This document covers the Logger, Neo4jOrmUtils, and error classes.

## Logger

The Logger class provides a centralized logging mechanism for Neo4j-ORM.

### LogLevel Enum

```typescript
enum LogLevel {
  ERROR = 0,  // Only log errors
  WARN = 1,   // Log errors and warnings
  INFO = 2,   // Log errors, warnings, and info messages
  DEBUG = 3   // Log everything
}
```

### Logger Instance

```typescript
static get instance(): Logger
```

Gets the singleton Logger instance.

**Returns:**
- The Logger instance

**Example:**
```typescript
const logger = Logger.instance;
logger.setLevel(LogLevel.DEBUG);
```

### setLevel

```typescript
setLevel(level: LogLevel): void
```

Sets the logging level.

**Parameters:**
- `level`: The log level to set

**Example:**
```typescript
// Set log level to DEBUG
Logger.instance.setLevel(LogLevel.DEBUG);

// Set log level to ERROR only
Logger.instance.setLevel(LogLevel.ERROR);
```

### Logging Methods

```typescript
debug(message: string, ...args: any[]): void
info(message: string, ...args: any[]): void
warn(message: string, ...args: any[]): void
error(message: string, ...args: any[]): void
```

Log messages at different levels.

**Parameters:**
- `message`: The message to log
- `args`: Additional arguments to log

**Example:**
```typescript
const logger = Logger.instance;

logger.debug('Querying database', { query: 'MATCH (n) RETURN n', params: {} });
logger.info('User created', { userId: '123' });
logger.warn('Deprecated method called', { method: 'oldMethod' });
logger.error('Database connection failed', error);
```

## Neo4jOrmUtils

The Neo4jOrmUtils class provides static utility methods.

### isEmptyObject

```typescript
static isEmptyObject(obj: any): boolean
```

Checks if an object is empty.

**Parameters:**
- `obj`: The object to check

**Returns:**
- `true` if the object is empty, `false` otherwise

**Example:**
```typescript
const empty = Neo4jOrmUtils.isEmptyObject({}); // true
const notEmpty = Neo4jOrmUtils.isEmptyObject({ name: 'John' }); // false
```

### camelToHuman

```typescript
static camelToHuman(camelCase: string): string
```

Converts a camelCase string to human-readable format.

**Parameters:**
- `camelCase`: The camelCase string

**Returns:**
- The human-readable string

**Example:**
```typescript
const human = Neo4jOrmUtils.camelToHuman('firstName'); // "First Name"
const human2 = Neo4jOrmUtils.camelToHuman('userEmailAddress'); // "User Email Address"
```

### camelToSnake

```typescript
static camelToSnake(camelCase: string): string
```

Converts a camelCase string to snake_case.

**Parameters:**
- `camelCase`: The camelCase string

**Returns:**
- The snake_case string

**Example:**
```typescript
const snake = Neo4jOrmUtils.camelToSnake('firstName'); // "first_name"
const snake2 = Neo4jOrmUtils.camelToSnake('userEmailAddress'); // "user_email_address"
```

### generateUuid

```typescript
static generateUuid(): string
```

Generates a UUID v4.

**Returns:**
- A UUID string

**Example:**
```typescript
const id = Neo4jOrmUtils.generateUuid(); // "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
```

### extractEntityFromRecord

```typescript
static extractEntityFromRecord(record: NodeRecord): any
```

Extracts entity properties from a Neo4j record.

**Parameters:**
- `record`: The Neo4j record

**Returns:**
- An object with entity properties

**Example:**
```typescript
const properties = Neo4jOrmUtils.extractEntityFromRecord(record);
```

### createSafeParams

```typescript
static createSafeParams(params: QueryParams): QueryParams
```

Creates a safe copy of query parameters, removing undefined values and functions.

**Parameters:**
- `params`: The original parameters

**Returns:**
- A safe copy of the parameters

**Example:**
```typescript
const params = {
  name: 'John',
  age: 30,
  address: undefined,
  getStatus: function() { return 'active'; }
};

const safeParams = Neo4jOrmUtils.createSafeParams(params);
// Result: { name: 'John', age: 30 }
```

### sanitizeIdentifier

```typescript
static sanitizeIdentifier(identifier: string): string
```

Sanitizes an identifier to prevent Cypher injection.

**Parameters:**
- `identifier`: The identifier to sanitize

**Returns:**
- The sanitized identifier

**Example:**
```typescript
const safe = Neo4jOrmUtils.sanitizeIdentifier('user-name'); // "username"
```

### sanitizeLabel

```typescript
static sanitizeLabel(label: string): string
```

Sanitizes a label to prevent Cypher injection.

**Parameters:**
- `label`: The label to sanitize

**Returns:**
- The sanitized label

**Example:**
```typescript
const safe = Neo4jOrmUtils.sanitizeLabel('User:Admin'); // "UserAdmin"
```

### sanitizeCondition

```typescript
static sanitizeCondition(condition: string): string
```

Sanitizes a query condition to prevent Cypher injection.

**Parameters:**
- `condition`: The condition to sanitize

**Returns:**
- The sanitized condition

**Example:**
```typescript
const safe = Neo4jOrmUtils.sanitizeCondition('n.name = "John"; MATCH (n) DELETE n;');
// Result: 'n.name = "John"'
```

### sanitizeParameters

```typescript
static sanitizeParameters(params: any): any
```

Sanitizes query parameters to prevent Cypher injection.

**Parameters:**
- `params`: The parameters to sanitize

**Returns:**
- The sanitized parameters

**Example:**
```typescript
const safe = Neo4jOrmUtils.sanitizeParameters({
  'name;': 'John',
  'age--': 30
});
// Result: { name: 'John', age: 30 }
```

## Error Classes

Neo4j-ORM provides several error classes for different types of errors.

### Neo4jORMError

```typescript
class Neo4jORMError extends Error
```

Base error class for all Neo4j-ORM errors.

**Constructor:**
```typescript
constructor(message: string)
```

**Example:**
```typescript
throw new Neo4jORMError('Something went wrong');
```

### ConnectionError

```typescript
class ConnectionError extends Neo4jORMError
```

Error related to database connection issues.

**Constructor:**
```typescript
constructor(message: string, public originalError?: Error)
```

**Example:**
```typescript
try {
  // Connection code...
} catch (error) {
  throw new ConnectionError('Failed to connect to Neo4j', error);
}
```

### QueryError

```typescript
class QueryError extends Neo4jORMError
```

Error related to query execution issues.

**Constructor:**
```typescript
constructor(
  message: string,
  public query?: string,
  public params?: any,
  public originalError?: Error
)
```

**Example:**
```typescript
try {
  // Query execution code...
} catch (error) {
  throw new QueryError(
    'Failed to execute query',
    'MATCH (n:User) RETURN n',
    { limit: 10 },
    error
  );
}
```

### EntityNotFoundError

```typescript
class EntityNotFoundError extends Neo4jORMError
```

Error thrown when an entity is not found.

**Constructor:**
```typescript
constructor(entityName: string, criteria?: any)
```

**Example:**
```typescript
if (!user) {
  throw new EntityNotFoundError('User', { id: '123' });
}
```

### MetadataError

```typescript
class MetadataError extends Neo4jORMError
```

Error related to entity metadata.

**Constructor:**
```typescript
constructor(message: string)
```

**Example:**
```typescript
throw new MetadataError('Invalid entity metadata');
```

### CompositeUniqueError

```typescript
class CompositeUniqueError extends Neo4jORMError
```

Error thrown when a composite unique constraint is violated.

**Constructor:**
```typescript
constructor(
  entityName: string,
  propertyNames: string[],
  values: Record<string, any>
)
```

**Example:**
```typescript
throw new CompositeUniqueError(
  'Employee',
  ['companyId', 'employeeNumber'],
  { companyId: 'company1', employeeNumber: 'E12345' }
);
```

## Operators

Neo4j-ORM provides operators for query conditions and updates.

### Query Operators (Op)

```typescript
const Op = {
  eq: Symbol('eq'),           // Equal
  ne: Symbol('ne'),           // Not equal
  gt: Symbol('gt'),           // Greater than
  gte: Symbol('gte'),         // Greater than or equal
  lt: Symbol('lt'),           // Less than
  lte: Symbol('lte'),         // Less than or equal
  in: Symbol('in'),           // In array
  notIn: Symbol('notIn'),     // Not in array
  like: Symbol('like'),       // Like pattern
  notLike: Symbol('notLike'), // Not like pattern
  contains: Symbol('contains'), // Contains substring
  startsWith: Symbol('startsWith'), // Starts with substring
  endsWith: Symbol('endsWith')    // Ends with substring
};
```

**Example:**
```typescript
const users = await userRepository.find({
  where: {
    age: { [Op.gt]: 21 },
    name: { [Op.contains]: 'John' },
    status: { [Op.in]: ['active', 'pending'] }
  }
});
```

### Update Operators (UpdateOp)

```typescript
const UpdateOp = {
  set: Symbol('set'),     // Set to value
  inc: Symbol('inc'),     // Increment by value
  dec: Symbol('dec'),     // Decrement by value
  push: Symbol('push'),   // Add to array
  pull: Symbol('pull')    // Remove from array
};
```

**Example:**
```typescript
await userRepository.update(userId, {
  loginCount: { [UpdateOp.inc]: 1 },
  lastLogin: { [UpdateOp.set]: new Date() },
  roles: { [UpdateOp.push]: 'editor' }
});
```

## Error Handling

Here's how to handle different types of errors:

```typescript
try {
  // Neo4j-ORM operations...
} catch (error) {
  if (error instanceof ConnectionError) {
    console.error('Connection Error:', error.message);
    // Handle connection issues
  } else if (error instanceof QueryError) {
    console.error('Query Error:', error.message);
    console.error('Query:', error.query);
    console.error('Parameters:', error.params);
    // Handle query execution issues
  } else if (error instanceof EntityNotFoundError) {
    console.error('Entity Not Found:', error.message);
    // Handle missing entity
  } else if (error instanceof MetadataError) {
    console.error('Metadata Error:', error.message);
    // Handle metadata issues
  } else if (error instanceof CompositeUniqueError) {
    console.error('Composite Unique Constraint Violated:', error.message);
    // Handle unique constraint violation
  } else if (error instanceof Neo4jORMError) {
    console.error('Neo4j-ORM Error:', error.message);
    // Handle other Neo4j-ORM errors
  } else {
    console.error('Unknown Error:', error);
    // Handle other errors
  }
}
```

## Logging Configuration

Configure the logger at the start of your application:

```typescript
import { Logger, LogLevel } from 'neo4j-orm';

// Set global log level
Logger.instance.setLevel(LogLevel.INFO);

// Different log levels for different environments
if (process.env.NODE_ENV === 'development') {
  Logger.instance.setLevel(LogLevel.DEBUG);
} else if (process.env.NODE_ENV === 'production') {
  Logger.instance.setLevel(LogLevel.ERROR);
}
```

This concludes the Utilities API reference.
