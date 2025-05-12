# Relationships Example

This example demonstrates how to define and work with relationships between entities in Neo4j-ORM.

## Setting Up Entities with Relationships

First, let's define our entities with their relationships:

```typescript
import { 
  DataSource, 
  Entity, 
  NodeId, 
  Property, 
  CreateDateColumn,
  UpdateDateColumn,
  Relationship,
  RelationshipProperty,
  Op
} from 'neo4j-orm';
import 'reflect-metadata';

// User entity
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false })
  name: string;

  @Property({ unique: true, nullable: false })
  email: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  // One-to-many relationship: User -> Posts
  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: () => Post,  // Using a function to avoid circular reference issues
    cascade: true        // Enable cascading save operations
  })
  posts: Post[];

  // Many-to-many relationship: User -> Categories (user follows categories)
  @Relationship({
    type: 'FOLLOWS',
    direction: 'OUT',
    target: () => Category
  })
  followedCategories: Category[];

  // Relationship with properties: User -> User (follows)
  @Relationship({
    type: 'FOLLOWS_USER',
    direction: 'OUT',
    target: () => User
  })
  following: UserFollow[];

  // Reverse relationship: users who follow this user
  @Relationship({
    type: 'FOLLOWS_USER',
    direction: 'IN',
    target: () => User
  })
  followers: UserFollow[];
}

// Post entity
@Entity()
class Post {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false })
  title: string;

  @Property({ nullable: false })
  content: string;

  @Property({ default: false })
  published: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  // Many-to-one relationship: Post -> User (author)
  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: () => User
  })
  author: User;

  // Many-to-many relationship: Post -> Categories
  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: () => Category
  })
  categories: Category[];

  // One-to-many relationship: Post -> Comments
  @Relationship({
    type: 'HAS_COMMENT',
    direction: 'OUT',
    target: () => Comment,
    cascade: true
  })
  comments: Comment[];
}

// Category entity
@Entity()
class Category {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false, unique: true })
  name: string;

  @Property({ nullable: true })
  description: string;

  // Many-to-many relationship: Category -> Posts
  @Relationship({
    type: 'HAS_POST',
    direction: 'OUT',
    target: () => Post
  })
  posts: Post[];

  // Many-to-many relationship: Category -> Users (followers)
  @Relationship({
    type: 'FOLLOWED_BY',
    direction: 'OUT',
    target: () => User
  })
  followers: User[];
}

// Comment entity
@Entity()
class Comment {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false })
  content: string;

  @CreateDateColumn()
  createdAt: Date;

  // Many-to-one relationship: Comment -> User (author)
  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: () => User
  })
  author: User;

  // Many-to-one relationship: Comment -> Post
  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: () => Post
  })
  post: Post;
}

// UserFollow class to represent the "FOLLOWS_USER" relationship with properties
class UserFollow {
  @RelationshipProperty()
  since: Date;

  @RelationshipProperty({ default: false })
  notificationsEnabled: boolean;

  // The target user being followed
  followedUser: User;
}

// Create a DataSource
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post, Category, Comment],
  synchronize: true
});

// Initialize database connection
async function initialize() {
  await dataSource.initialize();
  console.log('Connected to Neo4j database');
}
```

## Creating Entities with Relationships

### Creating One-to-Many Relationships

```typescript
async function createUserWithPosts() {
  const userRepository = dataSource.getRepository(User);
  const postRepository = dataSource.getRepository(Post);

  // Create a user
  const user = userRepository.create({
    name: 'John Doe',
    email: 'john@example.com'
  });

  // Create posts
  const post1 = postRepository.create({
    title: 'Getting Started with Neo4j',
    content: 'Neo4j is a graph database...',
    published: true
  });

  const post2 = postRepository.create({
    title: 'Advanced Graph Queries',
    content: 'In this post, we explore...',
    published: false
  });

  // Set the relationships
  post1.author = user;
  post2.author = user;
  user.posts = [post1, post2];

  // Save the user with cascading to posts
  await userRepository.save(user, { saveRelations: true });
  console.log('User with posts created');
  
  return user;
}
```

### Creating Many-to-Many Relationships

```typescript
async function createCategoriesAndAssignToPosts() {
  const categoryRepository = dataSource.getRepository(Category);
  const postRepository = dataSource.getRepository(Post);

  // Create categories
  const techCategory = categoryRepository.create({
    name: 'Technology',
    description: 'Articles about technology'
  });

  const dbCategory = categoryRepository.create({
    name: 'Databases',
    description: 'All about databases'
  });

  // Save categories
  await categoryRepository.save([techCategory, dbCategory]);

  // Find a post
  const post = await postRepository.findOne({
    where: { title: 'Getting Started with Neo4j' }
  });

  if (post) {
    // Assign categories to the post
    post.categories = [techCategory, dbCategory];
    await postRepository.save(post, { saveRelations: true });
    console.log('Categories assigned to post');
  }
  
  return { techCategory, dbCategory };
}
```

### Creating Relationships with Properties

```typescript
async function createUserFollowsRelationship() {
  const userRepository = dataSource.getRepository(User);

  // Find users
  const john = await userRepository.findOne({
    where: { email: 'john@example.com' }
  });

  // Create another user
  const jane = userRepository.create({
    name: 'Jane Smith',
    email: 'jane@example.com'
  });
  await userRepository.save(jane);

  if (john && jane) {
    // Create a follow relationship with properties
    const follow = new UserFollow();
    follow.followedUser = jane;
    follow.since = new Date();
    follow.notificationsEnabled = true;

    // Assign the relationship
    john.following = [follow];
    
    // Save the relationship
    await userRepository.save(john, { saveRelations: true });
    console.log('User follow relationship created');
  }
  
  return { john, jane };
}
```

## Reading Entities with Relationships

### Finding Entities with Direct Relationships

```typescript
async function findUserWithPosts() {
  const userRepository = dataSource.getRepository(User);

  // Find a user with their posts
  const user = await userRepository.findOne({
    where: { email: 'john@example.com' },
    relations: ['posts']
  });

  if (user) {
    console.log('User:', user.name);
    console.log('Posts:', user.posts.map(post => post.title));
  }
  
  return user;
}
```

### Finding Entities with Nested Relationships

```typescript
async function findPostWithAuthorAndComments() {
  const postRepository = dataSource.getRepository(Post);

  // Find a post with its author and comments, and each comment's author
  const post = await postRepository.findOne({
    where: { published: true },
    relations: ['author', 'comments', 'comments.author']
  });

  if (post) {
    console.log('Post:', post.title);
    console.log('Author:', post.author.name);
    console.log('Comments:', post.comments.length);
    
    post.comments.forEach(comment => {
      console.log(`- ${comment.author.name}: ${comment.content}`);
    });
  }
  
  return post;
}
```

### Finding Entities Based on Relationship Properties

```typescript
async function findUsersFollowingWithNotifications() {
  const userRepository = dataSource.getRepository(User);
  
  // This requires a custom query since we need to filter on relationship properties
  const queryBuilder = userRepository.createQueryBuilder();
  
  queryBuilder
    .match('u', User)
    .match({
      related: [
        { identifier: 'u' },
        { direction: 'out', name: 'FOLLOWS_USER', identifier: 'rel' },
        { identifier: 'followedUser', label: 'User' }
      ]
    })
    .where('rel.notificationsEnabled = true')
    .return('u, followedUser, rel.since as since')
    .orderBy('since', 'DESC');
  
  const result = await queryBuilder.getRaw();
  
  console.log('Users with notifications enabled:');
  result.records.forEach(record => {
    const user = record.get('u').properties;
    const followedUser = record.get('followedUser').properties;
    const since = record.get('since');
    
    console.log(`${user.name} follows ${followedUser.name} since ${since}`);
  });
  
  return result;
}
```

## Updating Entities with Relationships

### Adding to an Existing Relationship

```typescript
async function addCommentToPost() {
  const postRepository = dataSource.getRepository(Post);
  const userRepository = dataSource.getRepository(User);
  const commentRepository = dataSource.getRepository(Comment);

  // Find post and user
  const post = await postRepository.findOne({
    where: { title: 'Getting Started with Neo4j' },
    relations: ['comments']
  });

  const user = await userRepository.findOne({
    where: { email: 'jane@example.com' }
  });

  if (post && user) {
    // Create a new comment
    const comment = commentRepository.create({
      content: 'Great article! Very helpful.',
      author: user,
      post: post
    });

    // Add to the existing comments array
    if (!post.comments) {
      post.comments = [];
    }
    post.comments.push(comment);

    // Save the post with the new comment
    await postRepository.save(post, { saveRelations: true });
    console.log('Comment added to post');
  }
  
  return post;
}
```

### Updating Relationship Properties

```typescript
async function updateFollowRelationship() {
  const userRepository = dataSource.getRepository(User);

  // Find the user with their following relationships
  const john = await userRepository.findOne({
    where: { email: 'john@example.com' },
    relations: ['following', 'following.followedUser']
  });

  if (john && john.following && john.following.length > 0) {
    // Update the relationship properties
    john.following[0].notificationsEnabled = false;
    
    // Save the updated relationship
    await userRepository.save(john, { saveRelations: true });
    console.log('Follow relationship updated');
  }
  
  return john;
}
```

### Replacing Relationships

```typescript
async function replacePostCategories() {
  const postRepository = dataSource.getRepository(Post);
  const categoryRepository = dataSource.getRepository(Category);

  // Find post with existing categories
  const post = await postRepository.findOne({
    where: { title: 'Getting Started with Neo4j' },
    relations: ['categories']
  });

  // Create a new category
  const newCategory = categoryRepository.create({
    name: 'Graph Databases',
    description: 'Specifically about graph databases'
  });
  await categoryRepository.save(newCategory);

  if (post) {
    // Replace all categories with just the new one
    post.categories = [newCategory];
    
    // Save the post with the updated categories
    await postRepository.save(post, { saveRelations: true });
    console.log('Post categories replaced');
  }
  
  return post;
}
```

## Deleting Relationships and Entities

### Removing a Relationship

```typescript
async function removePostCategory() {
  const postRepository = dataSource.getRepository(Post);

  // Find post with categories
  const post = await postRepository.findOne({
    where: { title: 'Getting Started with Neo4j' },
    relations: ['categories']
  });

  if (post && post.categories && post.categories.length > 0) {
    // Remove the first category from the array
    post.categories = post.categories.slice(1);
    
    // Save the post with the updated categories
    await postRepository.save(post, { saveRelations: true });
    console.log('Category removed from post');
  }
  
  return post;
}
```

### Deleting an Entity with Cascading

```typescript
async function deleteUserWithCascade() {
  const userRepository = dataSource.getRepository(User);

  // Find the user
  const jane = await userRepository.findOne({
    where: { email: 'jane@example.com' }
  });

  if (jane) {
    // Delete the user (this will cascade to related entities if configured)
    await userRepository.remove(jane);
    console.log('User deleted with cascading');
    
    // Verify the user is deleted
    const deletedUser = await userRepository.findOne({
      where: { email: 'jane@example.com' }
    });
    
    console.log('User still exists:', deletedUser !== null);
  }
}
```

## Advanced Relationship Queries

### Finding Users by Post Category

```typescript
async function findUsersByPostCategory() {
  // This requires a custom query
  const result = await dataSource.query(`
    MATCH (c:Category {name: $categoryName})<-[:BELONGS_TO]-(p:Post)-[:AUTHORED_BY]->(u:User)
    RETURN DISTINCT u.name as userName, u.email as userEmail, count(p) as postCount
    ORDER BY postCount DESC
  `, { categoryName: 'Technology' });
  
  console.log('Users who have posted in the Technology category:');
  result.records.forEach(record => {
    console.log(`${record.get('userName')} (${record.get('userEmail')}): ${record.get('postCount')} posts`);
  });
  
  return result;
}
```

### Finding Posts with Complex Relationship Criteria

```typescript
async function findPostsWithComplexCriteria() {
  const queryBuilder = dataSource.createQueryBuilder();
  
  queryBuilder
    .match('p', Post)
    .match({
      related: [
        { identifier: 'p' },
        { direction: 'out', name: 'AUTHORED_BY' },
        { identifier: 'u', label: 'User' }
      ]
    })
    .match({
      related: [
        { identifier: 'p' },
        { direction: 'out', name: 'BELONGS_TO' },
        { identifier: 'c', label: 'Category' }
      ]
    })
    .where('p.published = true')
    .andWhere('c.name IN $categories')
    .andWhere('size((p)-[:HAS_COMMENT]->()) > $minComments')
    .with('p, u, collect(distinct c.name) as categories')
    .return('p.title as title, p.createdAt as date, u.name as author, categories')
    .orderBy('date', 'DESC')
    .neogmaQueryBuilder.getBindParam().add({
      categories: ['Technology', 'Databases'],
      minComments: 0
    });
  
  const result = await queryBuilder.getRaw();
  
  console.log('Posts meeting complex criteria:');
  result.records.forEach(record => {
    console.log(`${record.get('title')} by ${record.get('author')}`);
    console.log(`- Categories: ${record.get('categories').join(', ')}`);
    console.log(`- Date: ${record.get('date')}`);
  });
  
  return result;
}
```

## Complete Example

Here's a complete example that demonstrates working with relationships:

```typescript
async function main() {
  try {
    // Connect to the database
    await initialize();
    
    // Create entities with relationships
    const john = await createUserWithPosts();
    const categories = await createCategoriesAndAssignToPosts();
    const users = await createUserFollowsRelationship();
    
    // Read entities with relationships
    await findUserWithPosts();
    await findPostWithAuthorAndComments();
    await findUsersFollowingWithNotifications();
    
    // Update relationships
    await addCommentToPost();
    await updateFollowRelationship();
    await replacePostCategories();
    
    // Delete relationships and entities
    await removePostCategory();
    await deleteUserWithCascade();
    
    // Advanced queries
    await findUsersByPostCategory();
    await findPostsWithComplexCriteria();
    
    console.log('All relationship operations completed successfully');
  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Close the connection
    await dataSource.destroy();
    console.log('Connection closed');
  }
}

// Run the example
main().catch(console.error);
```

This concludes the Relationships examples. These patterns demonstrate how to work with various types of relationships in Neo4j-ORM.
