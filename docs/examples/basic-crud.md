# Basic CRUD Operations Example

This example demonstrates how to perform basic Create, Read, Update, and Delete (CRUD) operations using Neo4j-ORM.

## Setup

First, set up your project and define an entity:

```typescript
import { 
  DataSource, 
  Entity, 
  NodeId, 
  Property, 
  CreateDateColumn, 
  UpdateDateColumn,
  DeleteDateColumn
} from 'neo4j-orm';
import 'reflect-metadata';

// Define a User entity
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false })
  firstName: string;

  @Property({ nullable: false })
  lastName: string;

  @Property({ unique: true, nullable: false })
  email: string;

  @Property({ nullable: true })
  phoneNumber?: string;

  @Property({ default: 0 })
  loginCount: number;

  @Property({ default: false })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @DeleteDateColumn()
  deletedAt: Date;

  // A convenience getter to retrieve the full name
  get fullName(): string {
    return `${this.firstName} ${this.lastName}`;
  }
}

// Create a DataSource
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User],
  synchronize: true  // Auto-create constraints and indices
});

// Initialize database connection
async function initialize() {
  await dataSource.initialize();
  console.log('Connected to Neo4j database');
}
```

## Create Operations

### Creating an Entity

```typescript
async function createUser() {
  // Get the repository
  const userRepository = dataSource.getRepository(User);

  // Create a user instance
  const user = userRepository.create({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    isActive: true
  });

  // Save the user to the database
  await userRepository.save(user);
  console.log('User created:', user);
  
  return user;
}
```

### Creating Multiple Entities

```typescript
async function createMultipleUsers() {
  const userRepository = dataSource.getRepository(User);

  // Create multiple users
  const users = [
    userRepository.create({
      firstName: 'Alice',
      lastName: 'Smith',
      email: 'alice.smith@example.com'
    }),
    userRepository.create({
      firstName: 'Bob',
      lastName: 'Johnson',
      email: 'bob.johnson@example.com'
    }),
    userRepository.create({
      firstName: 'Carol',
      lastName: 'Williams',
      email: 'carol.williams@example.com'
    })
  ];

  // Save all users in one operation
  await userRepository.save(users);
  console.log('Multiple users created');
  
  return users;
}
```

## Read Operations

### Finding All Entities

```typescript
async function findAllUsers() {
  const userRepository = dataSource.getRepository(User);

  // Find all users
  const users = await userRepository.find();
  console.log(`Found ${users.length} users`);
  
  return users;
}
```

### Finding Entities with Conditions

```typescript
async function findUsersWithConditions() {
  const userRepository = dataSource.getRepository(User);

  // Find active users
  const activeUsers = await userRepository.find({
    where: { isActive: true }
  });
  console.log(`Found ${activeUsers.length} active users`);

  // Find users with specific email domain
  const companyUsers = await userRepository.find({
    where: {
      email: { [Op.contains]: '@example.com' }
    }
  });
  console.log(`Found ${companyUsers.length} company users`);

  // Find users with sorting and pagination
  const paginatedUsers = await userRepository.find({
    skip: 0,     // Skip 0 results (first page)
    take: 10,    // Take 10 results per page
    order: [['lastName', 'ASC'], ['firstName', 'ASC']]  // Sort by last name, then first name
  });
  console.log(`Found ${paginatedUsers.length} users for page 1`);
  
  return { activeUsers, companyUsers, paginatedUsers };
}
```

### Finding a Single Entity

```typescript
async function findOneUser() {
  const userRepository = dataSource.getRepository(User);

  // Find by email (unique property)
  const john = await userRepository.findOne({
    where: { email: 'john.doe@example.com' }
  });
  console.log('Found user by email:', john?.fullName);

  // Find by ID
  if (john) {
    const userById = await userRepository.findOneById(john.id);
    console.log('Found user by ID:', userById?.fullName);
  }
  
  return john;
}
```

### Counting Entities

```typescript
async function countUsers() {
  const userRepository = dataSource.getRepository(User);

  // Count all users
  const totalCount = await userRepository.count();
  console.log(`Total users: ${totalCount}`);

  // Count active users
  const activeCount = await userRepository.count({
    where: { isActive: true }
  });
  console.log(`Active users: ${activeCount}`);
  
  return { totalCount, activeCount };
}
```

## Update Operations

### Updating an Entity

```typescript
async function updateUser(userId: string) {
  const userRepository = dataSource.getRepository(User);

  // Find the user
  const user = await userRepository.findOneById(userId);
  if (!user) {
    console.log('User not found');
    return null;
  }

  // Update properties
  user.phoneNumber = '555-123-4567';
  user.isActive = true;
  
  // Save the updated user
  await userRepository.save(user);
  console.log('User updated:', user);
  
  return user;
}
```

### Updating an Entity with Partial Data

```typescript
async function updateUserPartial(userId: string) {
  const userRepository = dataSource.getRepository(User);

  // Update specific properties without loading the entity first
  await userRepository.update(userId, {
    phoneNumber: '555-987-6543',
    loginCount: { [UpdateOp.inc]: 1 }  // Increment login count by 1
  });
  
  // Verify the update
  const updatedUser = await userRepository.findOneById(userId);
  console.log('User updated partially:', updatedUser);
  
  return updatedUser;
}
```

### Updating Multiple Entities

```typescript
async function updateMultipleUsers() {
  const userRepository = dataSource.getRepository(User);

  // Find users to update
  const inactiveUsers = await userRepository.find({
    where: { isActive: false }
  });
  
  if (inactiveUsers.length === 0) {
    console.log('No inactive users found');
    return [];
  }

  // Update all inactive users
  for (const user of inactiveUsers) {
    user.isActive = true;
  }
  
  // Save all updates in one operation
  await userRepository.save(inactiveUsers);
  console.log(`${inactiveUsers.length} users activated`);
  
  return inactiveUsers;
}
```

### Upsert Operation (Create or Update)

```typescript
async function upsertUser() {
  const userRepository = dataSource.getRepository(User);

  // Upsert a user (create if not exists, update if exists)
  const upsertedUser = await userRepository.upsert(
    {
      email: 'david.brown@example.com',
      firstName: 'David',
      lastName: 'Brown',
      isActive: true
    },
    ['email']  // Use email to determine uniqueness
  );
  
  console.log('User upserted:', upsertedUser);
  
  return upsertedUser;
}
```

## Delete Operations

### Hard Delete (Permanent Removal)

```typescript
async function hardDeleteUser(userId: string) {
  const userRepository = dataSource.getRepository(User);

  // Find the user
  const user = await userRepository.findOneById(userId);
  if (!user) {
    console.log('User not found');
    return false;
  }

  // Permanently delete the user
  await userRepository.remove(user);
  console.log('User permanently deleted');
  
  // Verify deletion
  const deletedUser = await userRepository.findOneById(userId);
  console.log('User exists after deletion:', deletedUser !== null); // Should be false
  
  return true;
}
```

### Soft Delete (Mark as Deleted)

```typescript
async function softDeleteUser(userId: string) {
  const userRepository = dataSource.getRepository(User);

  // Find the user
  const user = await userRepository.findOneById(userId);
  if (!user) {
    console.log('User not found');
    return false;
  }

  // Soft delete the user
  await userRepository.softRemove(user);
  console.log('User soft deleted');
  
  // Verify soft deletion
  const regularFind = await userRepository.findOneById(userId);
  console.log('User found with regular find:', regularFind !== null); // Should be false
  
  // Find with deleted
  const withDeletedOptions = { withDeleted: true };
  const deletedUser = await userRepository.findOne({
    where: { id: userId },
    ...withDeletedOptions
  });
  
  console.log('User found with withDeleted option:', deletedUser !== null); // Should be true
  console.log('Deleted at:', deletedUser?.deletedAt);
  
  return true;
}
```

### Recovering a Soft-Deleted Entity

```typescript
async function recoverUser(userId: string) {
  const userRepository = dataSource.getRepository(User);

  // Find the soft-deleted user
  const withDeletedOptions = { withDeleted: true };
  const deletedUser = await userRepository.findOne({
    where: { id: userId },
    ...withDeletedOptions
  });
  
  if (!deletedUser) {
    console.log('Deleted user not found');
    return false;
  }

  // Recover the user
  await userRepository.recover(deletedUser);
  console.log('User recovered');
  
  // Verify recovery
  const recoveredUser = await userRepository.findOneById(userId);
  console.log('User successfully recovered:', recoveredUser !== null); // Should be true
  console.log('Recovered user:', recoveredUser);
  
  return true;
}
```

## Using QueryBuilder for Complex Queries

```typescript
async function findUsersWithQueryBuilder() {
  const userRepository = dataSource.getRepository(User);

  // Create a query builder
  const queryBuilder = userRepository.createQueryBuilder();

  // Build a complex query
  queryBuilder
    .match('u', User)
    .where('u.isActive = true')
    .andWhere('u.loginCount > 0')
    .orderBy('u.lastName', 'ASC')
    .limit(5)
    .return('u');

  // Execute the query
  const users = await queryBuilder.getMany<User>();
  console.log(`Found ${users.length} active users with logins`);
  
  return users;
}
```

## Running Raw Cypher Queries

```typescript
async function runRawQuery() {
  // Run a raw Cypher query
  const result = await dataSource.query(`
    MATCH (u:User)
    WHERE u.isActive = true
    RETURN u.firstName, u.lastName, u.email, u.loginCount
    ORDER BY u.loginCount DESC
    LIMIT 10
  `);
  
  console.log('Raw query result:', result.records.map(record => ({
    firstName: record.get('u.firstName'),
    lastName: record.get('u.lastName'),
    email: record.get('u.email'),
    loginCount: record.get('u.loginCount')
  })));
  
  return result;
}
```

## Using Transactions for Multiple Operations

```typescript
async function performTransactionalOperations() {
  // Execute operations in a transaction
  const result = await dataSource.transaction(async manager => {
    // Get repositories
    const userRepository = manager.getRepository(User);
    
    // Find an existing user
    const user = await userRepository.findOne({
      where: { email: 'john.doe@example.com' }
    });
    
    if (!user) {
      throw new Error('User not found');
    }
    
    // Update the user
    user.loginCount += 1;
    user.isActive = true;
    await userRepository.save(user);
    
    // Create a new user
    const newUser = userRepository.create({
      firstName: 'Emily',
      lastName: 'Davis',
      email: 'emily.davis@example.com',
      isActive: true
    });
    await userRepository.save(newUser);
    
    // Return results from the transaction
    return {
      updatedUser: user,
      newUser
    };
  });
  
  console.log('Transaction completed');
  console.log('Updated user:', result.updatedUser);
  console.log('New user:', result.newUser);
  
  return result;
}
```

## Complete Example

Here's a complete example that demonstrates all CRUD operations:

```typescript
async function main() {
  try {
    // Connect to the database
    await initialize();
    
    // Create operations
    const john = await createUser();
    await createMultipleUsers();
    
    // Read operations
    await findAllUsers();
    await findUsersWithConditions();
    await findOneUser();
    await countUsers();
    
    // Update operations
    await updateUser(john.id);
    await updateUserPartial(john.id);
    await updateMultipleUsers();
    await upsertUser();
    
    // Delete operations
    const alice = await userRepository.findOne({
      where: { email: 'alice.smith@example.com' }
    });
    
    if (alice) {
      await hardDeleteUser(alice.id);
    }
    
    const bob = await userRepository.findOne({
      where: { email: 'bob.johnson@example.com' }
    });
    
    if (bob) {
      await softDeleteUser(bob.id);
      await recoverUser(bob.id);
    }
    
    // Complex queries
    await findUsersWithQueryBuilder();
    await runRawQuery();
    
    // Transactional operations
    await performTransactionalOperations();
    
    console.log('All operations completed successfully');
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

## Error Handling

Here's how to handle errors in CRUD operations:

```typescript
async function errorHandlingExample() {
  const userRepository = dataSource.getRepository(User);
  
  try {
    // Attempt to create a user with a duplicate email
    const user1 = userRepository.create({
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com'  // Assume this email already exists
    });
    
    await userRepository.save(user1);
  } catch (error) {
    if (error instanceof QueryError) {
      console.error('Query error:', error.message);
      // Handle unique constraint violation
      console.log('A user with this email already exists');
    } else {
      console.error('Unexpected error:', error);
    }
  }
  
  try {
    // Attempt to find a non-existent user
    const nonExistentUser = await userRepository.findOneById('non-existent-id');
    
    if (!nonExistentUser) {
      console.log('User not found');
      // Handle the case when user isn't found
    }
  } catch (error) {
    console.error('Error finding user:', error);
  }
}
```

This concludes the Basic CRUD Operations examples. These patterns demonstrate how to use Neo4j-ORM for common database operations with entities.
  