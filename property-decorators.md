# Property Decorators API Reference

This document covers the decorators used to define properties on entity classes in Neo4j-ORM.

## @Property

```typescript
@Property(options?: PropertyOptions)
```

Marks a class property to be stored in the database as a node property.

**Parameters:**
- `options` (optional): Configuration options for the property

**Returns:**
- A property decorator function

**Default behavior:**
- Maps the property to a node property with the same name
- Uses the TypeScript type for data conversion

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ type: 'number', nullable: false, default: 0 })
  age: number;

  @Property({ unique: true })
  email: string;
}
```

### PropertyOptions Interface

```typescript
interface PropertyOptions {
  type?: string;          // Property type ('string', 'number', 'boolean', 'date', etc.)
  nullable?: boolean;     // Whether the property can be null (default: true)
  default?: any;          // Default value when not specified
  index?: boolean;        // Whether to create an index on this property
  unique?: boolean;       // Whether to create a unique constraint
}
```

## @CreateDateColumn

```typescript
@CreateDateColumn(options?: PropertyOptions)
```

Automatically sets the property to the current date when the entity is created.

**Parameters:**
- `options` (optional): Configuration options for the property

**Returns:**
- A property decorator function

**Default behavior:**
- Sets the property to the current date/time when the entity is first saved
- The property is not modified on subsequent updates

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @CreateDateColumn()
  createdAt: Date;
}
```

## @UpdateDateColumn

```typescript
@UpdateDateColumn(options?: PropertyOptions)
```

Automatically updates the property to the current date whenever the entity is updated.

**Parameters:**
- `options` (optional): Configuration options for the property

**Returns:**
- A property decorator function

**Default behavior:**
- Updates the property to the current date/time whenever the entity is saved
- The property is set on creation and updated on each update

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

## @VersionColumn

```typescript
@VersionColumn(options?: PropertyOptions)
```

Automatically increments the property value whenever the entity is updated, creating a version counter.

**Parameters:**
- `options` (optional): Configuration options for the property

**Returns:**
- A property decorator function

**Default behavior:**
- Initializes to 0 or 1 when the entity is created
- Increments by 1 each time the entity is updated

**Example:**
```typescript
@Entity()
class Document {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property()
  content: string;

  @VersionColumn()
  version: number;
}
```

## @DeleteDateColumn

```typescript
@DeleteDateColumn(options?: PropertyOptions)
```

Used for soft deletion. When an entity is soft-deleted, this property is set to the current date.

**Parameters:**
- `options` (optional): Configuration options for the property

**Returns:**
- A property decorator function

**Default behavior:**
- Null when the entity is active
- Set to the current date/time when the entity is soft-deleted
- Set back to null when the entity is recovered

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @DeleteDateColumn()
  deletedAt: Date;
}

// Later in your code
await userRepository.softRemove(user); // Sets deletedAt to current date
await userRepository.recover(user);    // Sets deletedAt back to null
```

## Data Types

Neo4j-ORM supports the following data types:

| TypeScript Type | Neo4j Type    | Notes                               |
|-----------------|---------------|-------------------------------------|
| `string`        | String        | UTF-8 encoded text                  |
| `number`        | Integer/Float | Numbers are stored as 64-bit values |
| `boolean`       | Boolean       | true/false values                   |
| `Date`          | DateTime      | ISO 8601 format                     |
| `Object`        | Map           | Stored as Neo4j maps                |
| `Array`         | List          | Stored as Neo4j lists               |

**Example with different types:**
```typescript
@Entity()
class Product {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ type: 'number' })
  price: number;

  @Property()
  available: boolean;

  @Property()
  tags: string[];

  @Property()
  metadata: {
    manufacturer: string;
    dimensions: {
      width: number;
      height: number;
      depth: number;
    };
  };

  @CreateDateColumn()
  createdAt: Date;
}
```

## Common Property Patterns

### Required Properties

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property({ nullable: false })
  firstName: string;

  @Property({ nullable: false })
  lastName: string;

  @Property({ nullable: false, unique: true })
  email: string;
}
```

### Properties with Default Values

```typescript
@Entity()
class Article {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property()
  content: string;

  @Property({ default: false })
  published: boolean;

  @Property({ default: 0 })
  viewCount: number;

  @Property({ default: [] })
  tags: string[];

  @Property({ default: { rating: 0, ratingCount: 0 } })
  stats: { rating: number; ratingCount: number };
}
```

### Timestamp Fields

```typescript
@Entity()
class Task {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property({ nullable: true })
  description?: string;

  @Property({ default: 'pending' })
  status: 'pending' | 'in_progress' | 'completed';

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @Property({ nullable: true })
  completedAt?: Date;
}
```

### Soft Delete Pattern

```typescript
@Entity()
class Customer {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ unique: true })
  email: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @DeleteDateColumn()
  deletedAt: Date;

  // Helper getter
  get isDeleted(): boolean {
    return !!this.deletedAt;
  }
}
```

## Best Practices

1. **Be explicit with types:**
   - Specify the `type` option when the automatic type detection might be ambiguous
   - This makes your schema more self-documenting

2. **Use the right special columns:**
   - `@CreateDateColumn()` for creation timestamps
   - `@UpdateDateColumn()` for last-updated timestamps
   - `@VersionColumn()` for optimistic concurrency control
   - `@DeleteDateColumn()` for soft deletion

3. **Set appropriate constraints:**
   - Use `nullable: false` for required properties
   - Add `unique: true` for properties that must be unique
   - Add `index: true` or `@Index()` for properties used in queries

4. **Default values:**
   - Provide sensible defaults using the `default` option
   - Be careful with object/array defaults (they're shared across instances)

5. **Naming conventions:**
   - Use consistent naming for timestamp fields (e.g., `createdAt`, `updatedAt`)
   - Consider prefixing boolean fields with "is" or "has" (e.g., `isActive`, `hasSubscription`)

## Common Issues and Solutions

### Default Objects and Arrays

**Problem:** When using object or array defaults, the same reference is shared across all instances.

```typescript
@Entity()
class Post {
  @Property({ default: [] }) // Same array shared by all instances!
  tags: string[];
}
```

**Solution:** Use a function to create a new instance each time:

```typescript
@Entity()
class Post {
  @Property({ default: () => [] }) // Creates a new array for each instance
  tags: string[];

  @Property({ default: () => ({ views: 0, likes: 0 }) })
  stats: { views: number; likes: number };
}
```

### Type Conversion Issues

If you're experiencing type conversion issues (e.g., dates stored as strings), explicitly specify the type:

```typescript
@Entity()
class Event {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ type: 'date' }) // Explicitly specify date type
  eventDate: Date;
}
```

### Enum Properties

For enum properties, consider using string literals or storing as strings:

```typescript
// Define the enum
enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

@Entity()
class Task {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property({ type: 'string' })
  status: TaskStatus;
}

// Or using string literals
@Entity()
class Task {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property()
  status: 'pending' | 'in_progress' | 'completed';
}
```

This concludes the Property Decorators API reference.
