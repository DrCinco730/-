You're right, there isn't a feature specifically called "inherits" in Neode, but inheritance/extension can be achieved using the `extend` method. Here's how to implement inheritance for your scenario with Person, User, and Teacher:

## Model Inheritance in Neode

Neode's `extend` method allows you to create a new model that inherits all properties and relationships from a parent model while adding additional properties specific to the child model.

```javascript
// First, define your base Person model
neode.model('Person', {
  person_id: {
    type: 'uuid',
    primary: true
  },
  name: {
    type: 'string',
    required: true
  },
  email: {
    type: 'string',
    unique: true
  },
  dateOfBirth: 'date'
});

// Extend Person to create User model
neode.extend('Person', 'User', {
  username: {
    type: 'string',
    required: true,
    unique: true
  },
  password: {
    type: 'string',
    required: true,
    hidden: true // Hide from JSON output
  },
  lastLogin: 'datetime'
});

// Extend Person to create Teacher model
neode.extend('Person', 'Teacher', {
  teacher_id: {
    type: 'string',
    required: true,
    unique: true
  },
  subject: {
    type: 'string',
    required: true
  },
  department: 'string',
  students: {
    type: 'nodes',
    relationship: 'TEACHES',
    direction: 'OUT',
    target: 'Student'
  }
});
```

### How It Works

When you use `extend`, Neode:

1. Clones the original model's schema
2. Merges in your new properties
3. Creates a new model with the combined schema
4. Adds the new label to the list of labels for this model

This means that a node created with the `Teacher` model will have both the `Person` and `Teacher` labels in Neo4j, along with all the properties from both schemas.

### Usage Example

```javascript
// Create a teacher - note that you use all properties from both Person and Teacher
neode.create('Teacher', {
  name: 'John Smith',
  email: 'john.smith@school.edu',
  dateOfBirth: new Date('1980-05-15'),
  teacher_id: 'T12345',
  subject: 'Mathematics',
  department: 'Science'
})
  .then(teacher => {
    console.log(teacher.get('name')); // John Smith
    console.log(teacher.get('subject')); // Mathematics
    
    // When converted to JSON, includes all properties from Person and Teacher
    return teacher.toJson();
  })
  .then(json => {
    console.log(json);
    // {
    //   _id: '...',
    //   _labels: ['Person', 'Teacher'],
    //   name: 'John Smith',
    //   email: 'john.smith@school.edu',
    //   dateOfBirth: '2023-05-15',
    //   teacher_id: 'T12345',
    //   subject: 'Mathematics',
    //   department: 'Science'
    // }
  });
```

### Finding Inherited Models

When querying, you can use either the parent or child label:

```javascript
// Find using the child model (Teacher)
neode.find('Teacher', 'teacher_id_value')
  .then(teacher => {
    // Handle teacher...
  });

// Find using the parent model (Person) - will return all Person nodes,
// including Teachers and Users
neode.all('Person')
  .then(people => {
    // Handle all people...
  });
```

This is how model inheritance works in Neode - it's a simple extension mechanism that preserves all the original model's properties while adding new ones.
