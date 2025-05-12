# Entity Decorators API Reference

This document covers the decorators used to define entities and their metadata in Neo4j-ORM.

## @Entity

```typescript
@Entity(options?: EntityOptions)
```

Marks a class as an entity (Neo4j node).

**Parameters:**
- `options` (optional): Configuration options for the entity

**Returns:**
- A class decorator function

**Default behavior:**
- Uses the class name as the Neo4j label
- Enables synchronization (automatic constraint/index creation)

**Example:**
```typescript
@Entity()
class User {
  // properties...
}
```

With options:

```typescript
@Entity({
  name: 'Person',          // Use 'Person' as the Neo4j label
  synchronize: false       // Disable automatic synchronization
})
class User {
  // properties...
}
```

### EntityOptions Interface

```typescript
interface EntityOptions {
  name?: string;           // Custom label name (defaults to class name)
  synchronize?: boolean;   // Whether to create constraints/indices (default: true)
}
```

## @Unique

```typescript
@Unique(propertyNames: string[])
```

Creates a composite unique constraint for the specified properties.

**Parameters:**
- `propertyNames`: Array of property names that form the unique constraint

**Returns:**
- A class decorator function

**Default behavior:**
- Creates a constraint that requires the combination of properties to be unique

**Example:**
```typescript
@Entity()
@Unique(['firstName', 'lastName', 'companyId'])
class Employee {
  @NodeId()
  id: string;

  @Property()
  firstName: string;

  @Property()
  lastName: string;

  @Property()
  companyId: string;

  // Other properties...
}
```

## @Index

```typescript
@Index(name?: string, options?: { unique?: boolean, columns?: string[] })
```

Creates an index for the entity or property.

**Parameters:**
- `name` (optional): Custom name for the index
- `options` (optional): Index options
  - `unique`: Whether the index enforces uniqueness
  - `columns`: Array of property names for a composite index

**Returns:**
- A class or property decorator function

**Default behavior:**
- When used on a property: Creates an index on that property
- When used on a class: Creates a composite index on the specified columns

**Example as property decorator:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  @Index()
  name: string;

  @Property()
  @Index('email_idx', { unique: true })
  email: string;
}
```

**Example as class decorator:**
```typescript
@Entity()
@Index('name_email_idx', { columns: ['name', 'email'] })
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property()
  email: string;
}
```

## NodeId

```typescript
@NodeId(options?: NodeIdOptions)
```

Marks a property as the primary identifier for the entity.

**Parameters:**
- `options` (optional): Configuration options for the node ID

**Returns:**
- A property decorator function

**Default behavior:**
- Marks the property as the primary key
- Does not auto-generate values unless specified

**Example:**
```typescript
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  // Other properties...
}
```

### NodeIdOptions Interface

```typescript
interface NodeIdOptions {
  generated?: boolean;      // Auto-generate UUID if not provided (default: false)
  type?: string;            // Property type (default: 'string')
  primary?: boolean;        // Whether this is the primary key (always true)
}
```

## Common Entity Patterns

### Basic Entity

```typescript
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property()
  name: string;

  @Property({ unique: true })
  email: string;
}
```

### Entity with Composite Unique Constraint

```typescript
@Entity()
@Unique(['firstName', 'lastName', 'birthDate'])
class Person {
  @NodeId({ generated: true })
  id: string;

  @Property()
  firstName: string;

  @Property()
  lastName: string;

  @Property()
  birthDate: Date;
}
```

### Entity with Indices

```typescript
@Entity()
@Index('name_email_idx', { columns: ['name', 'email'] })
class Customer {
  @NodeId({ generated: true })
  id: string;

  @Property()
  @Index()
  name: string;

  @Property()
  @Index('email_idx', { unique: true })
  email: string;

  @Property()
  @Index()
  country: string;
}
```

## Best Practices

1. **Always define a NodeId:**
   - Each entity should have a primary identifier
   - Consider using `generated: true` for automatic UUID generation

2. **Use meaningful names:**
   - Choose descriptive names for entities, matching your domain concepts
   - Custom entity names can be useful when integrating with existing data

3. **Add indices for frequently queried fields:**
   - Use `@Index()` on properties used in WHERE clauses
   - This improves query performance

4. **Use unique constraints when appropriate:**
   - Mark properties that should be unique with `{ unique: true }`
   - Use `@Unique([...])` for composite unique constraints

5. **Understand synchronization:**
   - The `synchronize: true` option automatically creates constraints and indices
   - This is convenient for development but use with caution in production
   - Consider using migrations for production environments

## Common Issues and Solutions

### Circular Dependencies

When two entities reference each other, you may encounter circular dependency issues.

**Problem:**
```typescript
// Error: Cannot access Post before initialization
@Entity()
class User {
  @NodeId()
  id: string;

  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: Post // Error: Post is not defined yet
  })
  posts: Post[];
}

@Entity()
class Post {
  @NodeId()
  id: string;

  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: User
  })
  author: User;
}
```

**Solution:** Use a function that returns the entity class:

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: () => Post // Function that returns Post
  })
  posts: Post[];
}
```

### Entity Not Found in DataSource

If you get an error about entities not being found, ensure they're properly registered.

**Problem:**
```typescript
// Error: Entity User is not registered in the DataSource
const dataSource = new DataSource({
  // ...connection options
  entities: [] // Missing entity classes
});
```

**Solution:** Register all entity classes:

```typescript
const dataSource = new DataSource({
  // ...connection options
  entities: [User, Post, Comment] // Include all entity classes
});
```

### Synchronization Issues

If constraints or indices aren't being created properly:

1. Check that `synchronize: true` is set in the DataSource options
2. Ensure property decorators are correctly applied
3. Verify that your Neo4j instance has the necessary permissions
4. For composite constraints, note that Neo4j Community Edition doesn't support them natively

This concludes the Entity Decorators API reference.