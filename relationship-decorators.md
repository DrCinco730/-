# Relationship Decorators API Reference

This document covers the decorators used to define relationships between entities in Neo4j-ORM.

## @Relationship

```typescript
@Relationship(options: RelationshipOptions)
```

Defines a relationship between two entities.

**Parameters:**
- `options`: Configuration options for the relationship

**Returns:**
- A property decorator function

**Default behavior:**
- Creates a reference to another entity or a collection of entities
- Does not automatically load the related entities unless `eager: true`

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: Post,
    cascade: true
  })
  posts: Post[];

  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: Company
  })
  company: Company;
}
```

### RelationshipOptions Interface

```typescript
interface RelationshipOptions {
  type: string;                              // Relationship type name in Neo4j
  direction: 'IN' | 'OUT' | 'NONE';          // Direction of the relationship
  target: Function | (() => Function);       // Target entity class
  cascade?: boolean | string[];              // Whether to cascade operations
  eager?: boolean;                           // Always load the relationship
  lazy?: boolean;                            // Load only when accessed
}
```

### Relationship Direction

The `direction` parameter specifies how the relationship is directed:

- `'OUT'`: The relationship goes from the current entity to the target entity
- `'IN'`: The relationship comes from the target entity to the current entity
- `'NONE'`: The relationship is undirected (bidirectional)

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  // User -[WORKS_AT]-> Company
  @Relationship({
    type: 'WORKS_AT',
    direction: 'OUT',
    target: Company
  })
  company: Company;

  // User <-[MANAGES]- Department
  @Relationship({
    type: 'MANAGES',
    direction: 'IN',
    target: Department
  })
  managedDepartments: Department[];

  // User -[FRIENDS_WITH]- User (undirected)
  @Relationship({
    type: 'FRIENDS_WITH',
    direction: 'NONE',
    target: 'User' // Self-reference
  })
  friends: User[];
}
```

### Loading Strategies

Neo4j-ORM provides different strategies for loading relationships:

1. **Standard loading:** Relationships are loaded explicitly when requested in `find` options
2. **Eager loading:** Relationships are always loaded (`eager: true`)
3. **Lazy loading:** Relationships are loaded on-demand when accessed (`lazy: true`)

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  // Always loaded with user
  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: Company,
    eager: true
  })
  company: Company;

  // Loaded on-demand when accessed
  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: Post,
    lazy: true
  })
  posts: Promise<Post[]>; // Note: lazy relationships return a Promise
}
```

### Cascading Operations

The `cascade` option allows operations to propagate to related entities:

- `true`: Cascade all operations (save, remove)
- `false`: Don't cascade any operations (default)
- `string[]`: Specify which operations to cascade, e.g., `['save']`

**Example:**
```typescript
@Entity()
class Post {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Relationship({
    type: 'HAS_COMMENT',
    direction: 'OUT',
    target: Comment,
    cascade: true // Cascade all operations
  })
  comments: Comment[];

  @Relationship({
    type: 'WRITTEN_BY',
    direction: 'OUT',
    target: User,
    cascade: ['save'] // Only cascade save operations
  })
  author: User;
}
```

With cascading enabled, when you save a post, its related comments will also be saved:

```typescript
const post = new Post();
post.title = 'My First Post';

const comment1 = new Comment();
comment1.text = 'Great post!';

const comment2 = new Comment();
comment2.text = 'I learned a lot!';

post.comments = [comment1, comment2];

// Save post and all its comments in one operation
await postRepository.save(post);
```

## @RelationshipProperty

```typescript
@RelationshipProperty(options?: RelationshipPropertyOptions)
```

Defines a property on a relationship.

**Parameters:**
- `options` (optional): Configuration options for the relationship property

**Returns:**
- A property decorator function

**Default behavior:**
- Maps a property to be stored on the relationship rather than on the node

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Relationship({
    type: 'RATED',
    direction: 'OUT',
    target: Product
  })
  ratedProducts: ProductRating[];
}

class ProductRating {
  @RelationshipProperty()
  rating: number;

  @RelationshipProperty()
  comment: string;

  @RelationshipProperty()
  ratedAt: Date;

  product: Product;
}
```

### RelationshipPropertyOptions Interface

```typescript
interface RelationshipPropertyOptions {
  type?: string;        // Property type
  nullable?: boolean;   // Whether the property can be null
  default?: any;        // Default value when not specified
}
```

## @RelationshipProperties

```typescript
@RelationshipProperties()
```

Marks an object property that contains relationship properties.

**Returns:**
- A property decorator function

**Default behavior:**
- Marks an object as containing properties to be stored on the relationship

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'FOLLOWS',
    direction: 'OUT',
    target: User
  })
  following: UserFollow[];
}

class UserFollow {
  @RelationshipProperties()
  properties: {
    since: Date;
    notificationsEnabled: boolean;
  };

  followedUser: User;
}
```

## Common Relationship Patterns

### One-to-One Relationship

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'HAS_PROFILE',
    direction: 'OUT',
    target: Profile,
    cascade: true
  })
  profile: Profile;
}

@Entity()
class Profile {
  @NodeId()
  id: string;

  @Property()
  bio: string;

  @Property()
  avatarUrl: string;

  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: User
  })
  user: User;
}
```

### One-to-Many Relationship

```typescript
@Entity()
class Author {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'WROTE',
    direction: 'OUT',
    target: Book,
    cascade: true
  })
  books: Book[];
}

@Entity()
class Book {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Relationship({
    type: 'WRITTEN_BY',
    direction: 'OUT',
    target: Author
  })
  author: Author;
}
```

### Many-to-Many Relationship

```typescript
@Entity()
class Student {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'ENROLLED_IN',
    direction: 'OUT',
    target: Course
  })
  courses: Course[];
}

@Entity()
class Course {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Relationship({
    type: 'HAS_STUDENT',
    direction: 'OUT',
    target: Student
  })
  students: Student[];
}
```

### Relationship with Properties

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'RATED',
    direction: 'OUT',
    target: Movie
  })
  ratedMovies: MovieRating[];
}

@Entity()
class Movie {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Relationship({
    type: 'RATED_BY',
    direction: 'OUT',
    target: User
  })
  ratings: MovieRating[];
}

class MovieRating {
  @RelationshipProperty()
  rating: number; // 1-5 stars

  @RelationshipProperty()
  comment: string;

  @RelationshipProperty()
  ratedAt: Date;

  movie: Movie;
  user: User;
}
```

### Self-Referencing Relationship

```typescript
@Entity()
class Person {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'PARENT_OF',
    direction: 'OUT',
    target: 'Person' // Self-reference using string
  })
  children: Person[];

  @Relationship({
    type: 'PARENT_OF',
    direction: 'IN',
    target: 'Person'
  })
  parents: Person[];

  @Relationship({
    type: 'MARRIED_TO',
    direction: 'NONE',
    target: 'Person'
  })
  spouse: Person;
}
```

For circular dependencies, use a function that returns the target entity:

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'FRIENDS_WITH',
    direction: 'NONE',
    target: () => User // Function that returns User
  })
  friends: User[];
}
```

## Loading Relationships

### Explicit Loading

To load relationships with a query, use the `relations` option:

```typescript
// Load user with their posts and company
const user = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts', 'company']
});

// Load user with nested relationships
const userWithNestedRelations = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts', 'posts.comments', 'posts.comments.author']
});
```

### Using QueryBuilder

For more complex relationship loading, use the QueryBuilder:

```typescript
const qb = userRepository.createQueryBuilder();

qb.match('u', User)
  .where('u.id = $id')
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED' },
      { identifier: 'p', label: 'Post' }
    ]
  })
  .return('u, collect(p) as posts')
  .neogmaQueryBuilder.getBindParam().add({ id: '123' });

const result = await qb.getRaw();
```

## Best Practices

1. **Choose the right direction:**
   - Consider the semantics of your domain when deciding on relationship directions
   - Use consistent naming conventions for your relationship types

2. **Use cascading appropriately:**
   - Enable cascading for parent-child relationships (e.g., `Post -> Comments`)
   - Be careful with bidirectional cascading to avoid infinite loops

3. **Consider loading strategies:**
   - Use `eager: true` only for relationships that are almost always needed
   - Use `lazy: true` for relationships that are rarely needed or contain large amounts of data

4. **Handle circular dependencies:**
   - Use function expressions for self-referencing relationships
   - For circular dependencies between entities, use the `() => EntityClass` syntax

5. **Use relationship properties:**
   - Store relationship-specific data using `@RelationshipProperty`
   - This is more efficient than creating intermediate entities

## Common Issues and Solutions

### Circular Dependencies

**Problem:** When two entities reference each other, TypeScript may complain about circular dependencies.

**Solution:** Use a function that returns the entity class:

```typescript
@Entity()
class User {
  // ...
  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: () => Post // Function that returns Post
  })
  posts: Post[];
}

@Entity()
class Post {
  // ...
  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: () => User // Function that returns User
  })
  author: User;
}
```

### Loading Relationships

**Problem:** Relationships aren't loaded automatically.

**Solution:** Either specify the relationships to load in `find` options, or use `eager: true`:

```typescript
// Option 1: Explicitly specify relations
const user = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts']
});

// Option 2: Make the relationship eager
@Relationship({
  type: 'AUTHORED',
  direction: 'OUT',
  target: Post,
  eager: true // Always loaded
})
posts: Post[];
```

### Infinite Cascading

**Problem:** Bidirectional relationships with cascading can cause infinite loops.

**Solution:** Limit cascade operations to one direction:

```typescript
@Entity()
class Post {
  // ...
  @Relationship({
    type: 'HAS_COMMENT',
    direction: 'OUT',
    target: Comment,
    cascade: true // Enable cascading from Post to Comment
  })
  comments: Comment[];
}

@Entity()
class Comment {
  // ...
  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: Post,
    cascade: false // Disable cascading from Comment to Post
  })
  post: Post;
}
```

This concludes the Relationship Decorators API reference.
