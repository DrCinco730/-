# Events and Subscribers API Reference

Neo4j-ORM provides an event system that allows you to execute code at specific points in an entity's lifecycle. There are two ways to use events: entity listeners (methods in the entity class) and event subscribers (separate classes that can listen to events from multiple entities).

## Entity Lifecycle Events

The following events are available during an entity's lifecycle:

1. **Insert Events:**
   - `beforeInsert`: Before a new entity is inserted into the database
   - `afterInsert`: After a new entity is inserted into the database

2. **Update Events:**
   - `beforeUpdate`: Before an existing entity is updated
   - `afterUpdate`: After an existing entity is updated

3. **Remove Events:**
   - `beforeRemove`: Before an entity is removed from the database
   - `afterRemove`: After an entity is removed from the database

4. **Soft Remove Events:**
   - `beforeSoftRemove`: Before an entity is soft-removed (marked as deleted)
   - `afterSoftRemove`: After an entity is soft-removed

5. **Recover Events:**
   - `beforeRecover`: Before a soft-removed entity is recovered
   - `afterRecover`: After a soft-removed entity is recovered

## Entity Listeners

Entity listeners are methods within the entity class that are decorated with event decorators:

### @BeforeInsert

```typescript
@BeforeInsert(): MethodDecorator
```

Executes the method before the entity is inserted.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @Property()
  name: string;

  @BeforeInsert()
  normalizeEmail() {
    this.email = this.email.toLowerCase().trim();
  }
}
```

### @AfterInsert

```typescript
@AfterInsert(): MethodDecorator
```

Executes the method after the entity is inserted.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @AfterInsert()
  logCreation() {
    console.log(`User created with ID: ${this.id}`);
  }
}
```

### @BeforeUpdate

```typescript
@BeforeUpdate(): MethodDecorator
```

Executes the method before the entity is updated.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @UpdateDateColumn()
  updatedAt: Date;

  @BeforeUpdate()
  validateEmail() {
    if (this.email && !this.email.includes('@')) {
      throw new Error('Invalid email format');
    }
  }
}
```

### @AfterUpdate

```typescript
@AfterUpdate(): MethodDecorator
```

Executes the method after the entity is updated.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @AfterUpdate()
  logUpdate() {
    console.log(`User ${this.id} was updated at ${new Date()}`);
  }
}
```

### @BeforeRemove

```typescript
@BeforeRemove(): MethodDecorator
```

Executes the method before the entity is removed.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @BeforeRemove()
  async backupData() {
    console.log(`Backing up data for user ${this.id} before removal`);
    // Perform backup logic...
  }
}
```

### @AfterRemove

```typescript
@AfterRemove(): MethodDecorator
```

Executes the method after the entity is removed.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @AfterRemove()
  logRemoval() {
    console.log(`User with email ${this.email} was removed`);
  }
}
```

### @BeforeSoftRemove

```typescript
@BeforeSoftRemove(): MethodDecorator
```

Executes the method before the entity is soft-removed.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @DeleteDateColumn()
  deletedAt: Date;

  @BeforeSoftRemove()
  notifyAboutDeletion() {
    console.log(`User ${this.id} will be soft-removed`);
  }
}
```

### @AfterSoftRemove

```typescript
@AfterSoftRemove(): MethodDecorator
```

Executes the method after the entity is soft-removed.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @DeleteDateColumn()
  deletedAt: Date;

  @AfterSoftRemove()
  logSoftRemoval() {
    console.log(`User ${this.id} was soft-removed at ${this.deletedAt}`);
  }
}
```

### @BeforeRecover

```typescript
@BeforeRecover(): MethodDecorator
```

Executes the method before a soft-removed entity is recovered.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @DeleteDateColumn()
  deletedAt: Date;

  @BeforeRecover()
  prepareForRecovery() {
    console.log(`Preparing to recover user ${this.id}`);
  }
}
```

### @AfterRecover

```typescript
@AfterRecover(): MethodDecorator
```

Executes the method after a soft-removed entity is recovered.

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @DeleteDateColumn()
  deletedAt: Date;

  @AfterRecover()
  notifyRecovery() {
    console.log(`User ${this.id} was recovered`);
  }
}
```

## Event Subscribers

Event subscribers are separate classes that can listen to events from one or more entity types:

### @EventSubscriber

```typescript
@EventSubscriber(): ClassDecorator
```

Marks a class as an event subscriber.

**Example:**
```typescript
@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  // Implementation details...
}
```

## EntitySubscriberInterface

The `EntitySubscriberInterface` defines methods that can be implemented to listen to entity events:

```typescript
interface EntitySubscriberInterface<Entity = any> {
  // Specify which entity this subscriber listens to
  listenTo?(): Function;
  
  // Insert events
  beforeInsert?(event: InsertEvent<Entity>): Promise<any> | any;
  afterInsert?(event: InsertEvent<Entity>): Promise<any> | any;
  
  // Update events
  beforeUpdate?(event: UpdateEvent<Entity>): Promise<any> | any;
  afterUpdate?(event: UpdateEvent<Entity>): Promise<any> | any;
  
  // Remove events
  beforeRemove?(event: RemoveEvent<Entity>): Promise<any> | any;
  afterRemove?(event: RemoveEvent<Entity>): Promise<any> | any;
  
  // Soft remove events
  beforeSoftRemove?(event: UpdateEvent<Entity>): Promise<any> | any;
  afterSoftRemove?(event: UpdateEvent<Entity>): Promise<any> | any;
  
  // Recover events
  beforeRecover?(event: UpdateEvent<Entity>): Promise<any> | any;
  afterRecover?(event: UpdateEvent<Entity>): Promise<any> | any;
}
```

### listenTo

```typescript
listenTo?(): Function
```

Specifies which entity class this subscriber listens to.

**Returns:**
- The entity class to listen to

**Default behavior:**
- If not specified, the subscriber listens to all entities

**Example:**
```typescript
@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  listenTo() {
    return User;
  }
  
  // Event handlers...
}
```

## Event Objects

Event handlers receive event objects that contain information about the operation:

### InsertEvent

```typescript
interface InsertEvent<Entity> {
  connection: DataSource;           // The DataSource instance
  queryRunner?: AdaptedQueryRunner; // The QueryRunner (if in transaction)
  manager: EntityManager;           // The EntityManager
  entity: Entity;                   // The entity being inserted
  metadata: any;                    // Entity metadata
}
```

### UpdateEvent

```typescript
interface UpdateEvent<Entity> {
  connection: DataSource;           // The DataSource instance
  queryRunner?: AdaptedQueryRunner; // The QueryRunner (if in transaction)
  manager: EntityManager;           // The EntityManager
  entity: Entity;                   // The entity being updated
  metadata: any;                    // Entity metadata
  databaseEntity: Entity;           // The entity as it exists in the database
  updatedColumns: any[];            // Columns that are being updated
  updatedRelations: any[];          // Relations that are being updated
}
```

### RemoveEvent

```typescript
interface RemoveEvent<Entity> {
  connection: DataSource;           // The DataSource instance
  queryRunner?: AdaptedQueryRunner; // The QueryRunner (if in transaction)
  manager: EntityManager;           // The EntityManager
  entity: Entity;                   // The entity being removed
  metadata: any;                    // Entity metadata
  databaseEntity: Entity;           // The entity as it exists in the database
}
```

## Complete Subscriber Example

```typescript
import {
  DataSource,
  Entity,
  NodeId,
  Property,
  CreateDateColumn,
  EventSubscriber,
  EntitySubscriberInterface,
  InsertEvent,
  UpdateEvent,
  RemoveEvent
} from 'neo4j-orm';

// Define the entity
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property({ unique: true })
  email: string;

  @Property()
  name: string;

  @Property({ default: false })
  isVerified: boolean;

  @CreateDateColumn()
  createdAt: Date;
}

// Define the subscriber
@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  // Listen to User entity events
  listenTo() {
    return User;
  }

  // Before insert
  async beforeInsert(event: InsertEvent<User>) {
    console.log('BEFORE USER INSERTED:', event.entity);
    
    // Normalize email
    if (event.entity.email) {
      event.entity.email = event.entity.email.toLowerCase().trim();
    }
  }

  // After insert
  async afterInsert(event: InsertEvent<User>) {
    console.log('AFTER USER INSERTED:', event.entity);
    
    // Example: Send welcome email
    const emailService = new EmailService();
    await emailService.sendWelcomeEmail(event.entity.email);
    
    // You can access the EntityManager to perform additional operations
    const logRepo = event.manager.getRepository(ActivityLog);
    await logRepo.save({
      action: 'USER_CREATED',
      entityId: event.entity.id,
      timestamp: new Date()
    });
  }

  // Before update
  async beforeUpdate(event: UpdateEvent<User>) {
    console.log('BEFORE USER UPDATED:', event.entity);
    
    // Check if email is changing
    if (event.entity.email !== event.databaseEntity.email) {
      console.log(`Email changing from ${event.databaseEntity.email} to ${event.entity.email}`);
      
      // Normalize the new email
      event.entity.email = event.entity.email.toLowerCase().trim();
      
      // Reset verification status when email changes
      event.entity.isVerified = false;
    }
  }

  // After update
  async afterUpdate(event: UpdateEvent<User>) {
    console.log('AFTER USER UPDATED:', event.entity);
    
    // Log the update
    const logRepo = event.manager.getRepository(ActivityLog);
    await logRepo.save({
      action: 'USER_UPDATED',
      entityId: event.entity.id,
      timestamp: new Date()
    });
  }

  // Before remove
  async beforeRemove(event: RemoveEvent<User>) {
    console.log('BEFORE USER REMOVED:', event.entity);
    
    // Backup user data before deletion
    const backupRepo = event.manager.getRepository(UserBackup);
    await backupRepo.save({
      originalId: event.entity.id,
      userData: JSON.stringify(event.entity),
      deletedAt: new Date()
    });
  }

  // After remove
  async afterRemove(event: RemoveEvent<User>) {
    console.log('AFTER USER REMOVED:', event.entity);
    
    // Cleanup related data
    const logRepo = event.manager.getRepository(ActivityLog);
    await logRepo.save({
      action: 'USER_DELETED',
      entityId: event.entity.id,
      timestamp: new Date()
    });
  }
}

// Register the subscriber
dataSource.registerSubscribers();
```

## Global Subscriber

You can create a subscriber that listens to events from all entities by not implementing the `listenTo` method:

```typescript
@EventSubscriber()
class GlobalSubscriber implements EntitySubscriberInterface {
  // No listenTo method, so it listens to all entities
  
  async beforeInsert(event: InsertEvent<any>) {
    console.log(`BEFORE ENTITY INSERTED: ${event.entity.constructor.name}`);
    // Add common behavior for all entities
  }
  
  async afterInsert(event: InsertEvent<any>) {
    console.log(`AFTER ENTITY INSERTED: ${event.entity.constructor.name}`);
    // Add common behavior for all entities
  }
}
```

## Registering Subscribers

Subscribers need to be registered with the DataSource to be active:

```typescript
// Create DataSource
const dataSource = new DataSource({
  // connection options...
});

// Initialize DataSource (registers subscribers)
await dataSource.initialize();

// Alternatively, explicitly register subscribers
dataSource.registerSubscribers();
```

The DataSource automatically registers all classes decorated with `@EventSubscriber()` when initialized.

## Event Flow

When an entity is saved, updated, or removed, events are triggered in this order:

1. Entity listener methods are called first
2. Subscriber methods are called after

For example, during entity insertion:

1. Entity's `@BeforeInsert` methods are called
2. Subscribers' `beforeInsert` methods are called
3. The entity is inserted into the database
4. Entity's `@AfterInsert` methods are called
5. Subscribers' `afterInsert` methods are called

## Best Practices

1. **Use entity listeners for simple operations:**
   - Normalizing data
   - Setting default values
   - Validating entity state

2. **Use subscribers for complex operations:**
   - Sending notifications
   - Creating related entities
   - Logging to external systems
   - Operations that require dependency injection

3. **Avoid infinite loops:**
   - Be careful not to trigger the same event again in an event handler
   - For example, don't update an entity in its `afterUpdate` handler

4. **Handle errors properly:**
   - If an event handler throws an error, the operation will be aborted
   - Use try/catch in event handlers if you want to log errors without aborting

5. **Keep subscribers focused:**
   - Create separate subscribers for different concerns
   - Follow the single responsibility principle

6. **Use async/await for asynchronous operations:**
   - Event handlers can be async functions
   - This allows you to perform database operations or call external services

## Common Patterns

### Automatic Timestamps

```typescript
@Entity()
class BaseEntity {
  @NodeId({ generated: true })
  id: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

@Entity()
class User extends BaseEntity {
  @Property()
  name: string;
  
  // Inherits id, createdAt, and updatedAt
}
```

### Data Normalization

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @BeforeInsert()
  @BeforeUpdate()
  normalizeEmail() {
    if (this.email) {
      this.email = this.email.toLowerCase().trim();
    }
  }
}
```

### Data Validation

```typescript
@Entity()
class Product {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ type: 'number' })
  price: number;

  @BeforeInsert()
  @BeforeUpdate()
  validatePrice() {
    if (this.price < 0) {
      throw new Error('Price cannot be negative');
    }
  }
}
```

### Logging and Auditing

```typescript
@EventSubscriber()
class AuditSubscriber implements EntitySubscriberInterface {
  constructor(private readonly auditService: AuditService) {}

  async afterInsert(event: InsertEvent<any>) {
    await this.auditService.log({
      action: 'INSERT',
      entityType: event.entity.constructor.name,
      entityId: event.entity.id,
      timestamp: new Date(),
      data: { ...event.entity }
    });
  }

  async afterUpdate(event: UpdateEvent<any>) {
    await this.auditService.log({
      action: 'UPDATE',
      entityType: event.entity.constructor.name,
      entityId: event.entity.id,
      timestamp: new Date(),
      data: { 
        before: { ...event.databaseEntity },
        after: { ...event.entity }
      }
    });
  }

  async afterRemove(event: RemoveEvent<any>) {
    await this.auditService.log({
      action: 'DELETE',
      entityType: event.entity.constructor.name,
      entityId: event.entity.id,
      timestamp: new Date(),
      data: { ...event.databaseEntity }
    });
  }
}
```

### Auto-Generated Slugs

```typescript
@Entity()
class Article {
  @NodeId()
  id: string;

  @Property()
  title: string;

  @Property({ unique: true })
  slug: string;

  @BeforeInsert()
  generateSlug() {
    if (this.title && !this.slug) {
      this.slug = this.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
    }
  }
}
```

This concludes the Events and Subscribers API reference.