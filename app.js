// ==========================================
// 1. DATA (Curriculum & Language Configs)
// ==========================================
const languagesData = {
  python: {
    id: 'python', name: 'Python', icon: '<i class="fa-brands fa-python text-blue-400"></i>', ext: 'py',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'py-l1', title: 'Hello World',
            theory: `Welcome to Python! Python is widely considered one of the best languages for beginners due to its clean, highly readable syntax that resembles plain English.\n\nIn programming, we constantly need to output information to the screen. In Python, we achieve this using a built-in function called **print()**.\n\nWhen you want to print text, you must tell the computer exactly where the text begins and ends by wrapping our text in quotation marks. Text wrapped in quotes is referred to as a **String**.`,
            instructions: `Use the print function to output the String "Hello World" to the console.`,
            initialCode: `# Write your code below\n`,
            solution: `print("Hello World")`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('print("helloworld")') || c.replace(/\s/g, '').toLowerCase().includes("print('helloworld')") || c.replace(/\s/g, '').toLowerCase().includes('print("helloworld!")') || c.replace(/\s/g, '').toLowerCase().includes('print("hello,world")'),
            successMsg: `Awesome! You've written your first Python program.`,
            errorMsg: `Make sure you use print() and put "Hello World" inside quotes.`
          },
          {
            id: 'py-l2', title: 'Variables & Data',
            theory: `Programs are useless if they can't remember information. **Variables** are like labeled containers in your computer's RAM that store data.\n\nIn Python, creating a variable is incredibly simple: you just invent a name, use the equals sign (**=**), and assign it a value. Python uses **Dynamic Typing**, meaning you don't have to explicitly tell Python whether you are storing a number or a string.\n\n**Rules:** No spaces allowed in names, and they cannot start with numbers.`,
            instructions: `Create a variable named 'age' and assign it the number 25. On the very next line, use print() to display the variable 'age' (Do not put quotes around the word age!).`,
            initialCode: `# Create age variable below\n\n# Print age below\n`,
            solution: `age = 25\nprint(age)`,
            validate: (c) => { const cl = c.replace(/\s/g, '').toLowerCase(); return cl.includes('age=25') && cl.includes('print(age)'); },
            successMsg: `Perfect! Variables are the fundamental building blocks.`,
            errorMsg: `Did you create 'age = 25' and use 'print(age)'? Make sure there are NO quotes around 'age'.`
          }
        ]
      },
      {
        level: 'Level 2: Data Structures',
        lessons: [
          {
            id: 'py-l3', title: 'Lists & Arrays',
            theory: `**Lists** (often called Arrays) allow you to store multiple items in a single, ordered variable container. They are created using square brackets **[]**, and items are separated by commas.\n\nExample:\n**inventory = ["Sword", "Shield", "Potion"]**\n\nLists are highly flexible in Python and can hold strings, numbers, or both!`,
            instructions: `Create a list named 'items' containing the string "Apple" and the string "Banana". Then, print the list.`,
            initialCode: `# Create your list below\n`,
            solution: `items = ["Apple", "Banana"]\nprint(items)`,
            validate: (c) => c.toLowerCase().includes('apple') && c.toLowerCase().includes('banana') && c.includes('['),
            successMsg: `Great job! You made your first list.`,
            errorMsg: `Make sure you create a list using square brackets [] containing both "Apple" and "Banana".`
          },
          {
            id: 'py-l4', title: 'Dictionaries',
            theory: `Sometimes you need more structure. **Dictionaries** store data in "Key-Value" pairs. Think of a real dictionary: you look up a word (the Key) to find the definition (the Value). Dictionaries are created using curly braces **{}**.\n\nExample:\n**player = {"name": "Alice", "score": 100}**\n\nYou can access Alice's score by typing **print(player["score"])**.`,
            instructions: `Create a dictionary named 'user'. Give it a key "username" with the value "Admin", and a key "role" with the value "Owner". Print the dictionary.`,
            initialCode: `# Create dictionary below\n`,
            solution: `user = {"username": "Admin", "role": "Owner"}\nprint(user)`,
            validate: (c) => c.includes('{') && c.includes('}') && c.toLowerCase().includes('admin') && c.toLowerCase().includes('owner'),
            successMsg: `Dictionaries mastered! These are crucial for handling JSON data later.`,
            errorMsg: `Did you use curly braces {} and include both "username" and "role"?`
          }
        ]
      },
      {
        level: 'Level 3: Architecture',
        lessons: [
          {
            id: 'py-l5', title: 'Functions',
            theory: `If you find yourself writing the exact same chunk of code over and over, you should wrap it in a **Function**. Functions are reusable blocks of code that only run when you call them.\n\nIn Python, you define a function using the **def** keyword.\n\nExample:\n**def say_hi(name):**\n    **print("Hi " + name)**`,
            instructions: `Define a function named 'multiply' that takes two parameters: 'a' and 'b'. Inside the function, return the result of a * b.`,
            initialCode: `# Define function below\n\n`,
            solution: `def multiply(a, b):\n    return a * b`,
            validate: (c) => c.replace(/\s/g, '').includes('defmultiply(a,b):') && c.replace(/\s/g, '').includes('returna*b'),
            successMsg: `Function defined! Code reusability unlocked.`,
            errorMsg: `Make sure you use 'def multiply(a, b):' and 'return a * b'. Watch your indentation!`
          },
          {
            id: 'py-l6', title: 'Classes & OOP',
            theory: `Object-Oriented Programming (OOP) is a massive paradigm shift. Instead of just writing top-to-bottom scripts, you create your own custom data structures called **Classes**.\n\nA Class is a blueprint. In Python, class functions must always take **self** as their first parameter.`,
            instructions: `Create a class named 'Robot'. Inside it, define a function named 'beep' that takes 'self' as a parameter and returns the string "Beep Boop".`,
            initialCode: `# Define your class below\n`,
            solution: `class Robot:\n    def beep(self):\n        return "Beep Boop"`,
            validate: (c) => c.includes('class Robot:') && c.includes('def beep(self):') && c.includes('Beep Boop'),
            successMsg: `OOP concepts grasped! You built a blueprint.`,
            errorMsg: `Did you write 'class Robot:' and 'def beep(self):' inside of it?`
          }
        ]
      },
      {
        level: 'Level 4: Advanced Logic',
        lessons: [
          {
            id: 'py-l7', title: 'Error Handling',
            theory: `Programs crash. It's a fact of life. But a good program handles crashes gracefully using **try/except** blocks.\n\nIf the code inside the **try** block causes an error (like dividing by zero), Python immediately jumps to the **except** block instead of crashing the entire script.`,
            instructions: `Write a 'try:' block that contains 'x = 1 / 0'. Below it, write an 'except:' block that prints "Error occurred".`,
            initialCode: `# Write try/except below\n`,
            solution: `try:\n    x = 1 / 0\nexcept:\n    print("Error occurred")`,
            validate: (c) => c.includes('try:') && c.includes('except:') && c.toLowerCase().includes('error occurred'),
            successMsg: `Crash averted! Your program is now robust.`,
            errorMsg: `Make sure you have a 'try:' block and an 'except:' block!`
          },
          {
            id: 'py-l8', title: 'List Comprehensions',
            theory: `Python is famous for **List Comprehensions**, a highly elegant way to generate lists in a single line of code instead of writing a clunky for-loop.\n\nExample: To get numbers 0-4, you can write: **nums = [x for x in range(5)]**`,
            instructions: `Create a variable named 'squares' using a list comprehension. It should equal '[x * x for x in [1, 2, 3]]'. Print 'squares'.`,
            initialCode: `# Create list comprehension below\n`,
            solution: `squares = [x * x for x in [1, 2, 3]]\nprint(squares)`,
            validate: (c) => c.replace(/\s/g, '').includes('squares=[x*xforxin[1,2,3]]') && c.replace(/\s/g, '').includes('print(squares)'),
            successMsg: `Pythonic! That is how professionals write lists.`,
            errorMsg: `Did you write squares = [x * x for x in [1, 2, 3]] and print it?`
          }
        ]
      },
      {
        level: 'Level 5: Algorithms',
        lessons: [
          {
            id: 'py-l9', title: 'Lambda Functions',
            theory: `Sometimes you need a tiny, throwaway function that you only use once. Python allows you to write one-line, nameless functions called **Lambdas**.\n\nExample:\n**double = lambda x: x * 2**`,
            instructions: `Create a variable 'add_ten' that equals 'lambda x: x + 10'. Then print 'add_ten(5)'.`,
            initialCode: `# Write lambda below\n`,
            solution: `add_ten = lambda x: x + 10\nprint(add_ten(5))`,
            validate: (c) => c.includes('lambda') && c.includes('+ 10') && c.includes('print('),
            successMsg: `Excellent! Lambdas are heavily used in data science (Pandas).`,
            errorMsg: `Make sure you assign a lambda to 'add_ten' and print its result!`
          },
          {
            id: 'py-l10', title: 'Recursion',
            theory: `Now for a true computer science challenge: **Recursion**. Recursion happens when a function calls *itself* from inside its own code.\n\nTo calculate the factorial of 5 (5!), you multiply 5 * 4 * 3 * 2 * 1. A recursive function can solve this by multiplying the number by the factorial of the number minus one, until it hits 1 (the base case).`,
            instructions: `Write a recursive function named 'factorial' that takes 'n'. If n is 1, return 1. Otherwise, return n * factorial(n - 1).`,
            initialCode: `# Write recursive function below\n`,
            solution: `def factorial(n):\n    if n == 1:\n        return 1\n    return n * factorial(n - 1)`,
            validate: (c) => c.includes('def factorial(') && c.replace(/\s/g, '').includes('return1') && c.replace(/\s/g, '').includes('n*factorial(n-1)'),
            successMsg: `Mind-bending! You successfully wrote a recursive algorithm.`,
            errorMsg: `Make sure the function calls itself using 'n * factorial(n - 1)'!`
          }
        ]
      }
    ]
  },

  javascript: {
    id: 'javascript', name: 'JavaScript', icon: '<i class="fa-brands fa-js text-yellow-400"></i>', ext: 'js',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'js-l1', title: 'Hello World',
            theory: `JavaScript is the undisputed language of the web. It provides logic, interactivity, and brainpower, running directly inside your browser.\n\nTo print messages behind the scenes, we use the browser's developer console with the **console.log()** command.\n\nAny text you want to print must be wrapped in quotation marks ("String"). JS traditionally uses semicolons (**;**) at the ends of lines.`,
            instructions: `Use console.log() to output "Hello World" to the console.`,
            initialCode: `// Write your code below\n`,
            solution: `console.log("Hello World");`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('console.log("helloworld') || c.replace(/\s/g, '').toLowerCase().includes("console.log('helloworld"),
            successMsg: `Awesome! You wrote your first JavaScript program.`,
            errorMsg: `Make sure you use console.log() and put "Hello World" inside quotes.`
          },
          {
            id: 'js-l2', title: 'Variables (Let & Const)',
            theory: `Variables store data that your website needs to remember.\n\nModern JavaScript uses two ways to declare variables safely:\n1. **let**: Use 'let' when you know the value will change later (like a score).\n2. **const**: Use 'const' when a value should NEVER change.\n\nNever use the old **var** keyword in modern code.`,
            instructions: `Create a variable named 'age' using the 'let' keyword and set it to 25. Then print it using console.log().`,
            initialCode: `// Create age variable below\n\n// Print age below\n`,
            solution: `let age = 25;\nconsole.log(age);`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('letage=25') && c.replace(/\s/g, '').toLowerCase().includes('console.log(age)'),
            successMsg: `Perfect! Variables are working beautifully.`,
            errorMsg: `Did you use 'let age = 25;' and 'console.log(age);'?`
          }
        ]
      },
      {
        level: 'Level 2: Modern ES6',
        lessons: [
          {
            id: 'js-l3', title: 'Arrow Functions',
            theory: `In modern JavaScript, the traditional 'function() {}' syntax is often replaced by **Arrow Functions**. Arrow functions are shorter, cleaner, and handle the 'this' keyword much more predictably.\n\nExample:\n**const sayHi = (name) => { console.log("Hi " + name); };**`,
            instructions: `Create a const arrow function named 'add' that takes parameters 'a' and 'b'. Inside the block, return a + b;`,
            initialCode: `// Write arrow function below\n`,
            solution: `const add = (a, b) => {\n  return a + b;\n};`,
            validate: (c) => c.replace(/\s/g, '').includes('constadd=(a,b)=>{') || c.replace(/\s/g, '').includes('constadd=(a,b)=>a+b'),
            successMsg: `ES6 Syntax nailed! Arrow functions are essential.`,
            errorMsg: `Did you write 'const add = (a, b) => { return a + b; }'?`
          },
          {
            id: 'js-l4', title: 'Array Mapping',
            theory: `When you have an array of data and you want to modify every item (like adding tax to prices), modern JS uses the **.map()** array method instead of 'for' loops.\n\nMap takes a function, runs it on every item, and returns a brand new array.`,
            instructions: `You have an array called 'nums'. Create a new const named 'doubled' that equals nums.map(n => n * 2). Console.log it.`,
            initialCode: `const nums = [1, 2, 3];\n// Map it below\n`,
            solution: `const nums = [1, 2, 3];\nconst doubled = nums.map(n => n * 2);\nconsole.log(doubled);`,
            validate: (c) => c.replace(/\s/g, '').includes('nums.map(') && c.includes('*') && c.includes('console.log(doubled)'),
            successMsg: `Functional programming achieved! .map() is used everywhere.`,
            errorMsg: `Make sure you use nums.map() and multiply the element by 2!`
          }
        ]
      },
      {
        level: 'Level 3: Objects & DOM',
        lessons: [
          {
            id: 'js-l5', title: 'Object Destructuring',
            theory: `Extracting data from complex objects used to take many lines of code. **Destructuring** allows you to pull properties out of an object and assign them to variables in a single line.\n\nExample:\n**const { name, age } = userProfile;**`,
            instructions: `You have an object called 'player'. Use destructuring to pull 'score' out of it: 'const { score } = player;'. Print score.`,
            initialCode: `const player = { name: "Alice", score: 50 };\n// Destructure below\n`,
            solution: `const { score } = player;\nconsole.log(score);`,
            validate: (c) => c.replace(/\s/g, '').includes('const{score}=player;') && c.includes('console.log(score)'),
            successMsg: `Destructuring mastered! It keeps code super clean.`,
            errorMsg: `Did you use 'const { score } = player;' ?`
          },
          {
            id: 'js-l6', title: 'Template Literals',
            theory: `Merging text and variables used to require clunky plus signs: *"Hi " + name + "!"*.\n\n**Template Literals** use backticks (the key above Tab) and dollar-sign brackets **\${}** to inject variables directly into strings cleanly.`,
            instructions: `Create a const 'name' set to "Bob". Then use console.log and backticks to print \`Hello \${name}\`.`,
            initialCode: `// Write template literal below\n`,
            solution: `const name = "Bob";\nconsole.log(\`Hello \${name}\`);`,
            validate: (c) => c.includes('`Hello ${') && c.includes('}`'),
            successMsg: `Template literals are a massive time-saver!`,
            errorMsg: `Did you use backticks (\`) and \${name} inside them?`
          }
        ]
      },
      {
        level: 'Level 4: Asynchronous JS',
        lessons: [
          {
            id: 'js-l7', title: 'Promises',
            theory: `JS is single-threaded. If it waits for a database, the whole site freezes! To fix this, we use **Promises**.\n\nA Promise is a guarantee that JS will return a value eventually, allowing code to keep running. We use '.then()' to handle the result when it arrives.`,
            instructions: `You are given a simulated fakeAPI(). Chain a '.then(res => console.log(res))' to it to print the data when it arrives.`,
            initialCode: `const fakeAPI = () => Promise.resolve("Data Loaded");\n// Call fakeAPI().then(...) below\n`,
            solution: `fakeAPI().then(res => console.log(res));`,
            validate: (c) => c.includes('.then(') && c.includes('console.log('),
            successMsg: `Promises handled! You are managing async operations.`,
            errorMsg: `Did you chain .then() to fakeAPI()?`
          },
          {
            id: 'js-l8', title: 'Async / Await',
            theory: `Chaining '.then()' can get messy. Modern JS uses **async/await** to make asynchronous code look like normal, top-to-bottom synchronous code.\n\nYou simply put the word 'async' before the function, and 'await' before the API call.`,
            instructions: `Create an 'async' arrow function named 'fetchData'. Inside, create a const 'res' that 'await's 'fakeApi()'.`,
            initialCode: `const fakeApi = () => Promise.resolve("Data");\n// Write async function below\n`,
            solution: `const fetchData = async () => {\n  const res = await fakeApi();\n};`,
            validate: (c) => c.includes('async ') && c.replace(/\s/g, '').includes('constres=awaitfakeApi()'),
            successMsg: `You are now a master of time! Async/Await is critical.`,
            errorMsg: `Did you define 'const fetchData = async () =>' and 'await fakeApi()'?`
          }
        ]
      },
      {
        level: 'Level 5: Functional Patterns',
        lessons: [
          {
            id: 'js-l9', title: 'Array Filtering',
            theory: `Just like .map(), **.filter()** is a powerful functional array method. It creates a new array filled ONLY with elements that pass a test (where the function returns true).`,
            instructions: `You have an array of 'scores'. Create a const 'highScores' equal to scores.filter(s => s > 50). Print it.`,
            initialCode: `const scores = [30, 80, 45, 90];\n// Filter it below\n`,
            solution: `const highScores = scores.filter(s => s > 50);\nconsole.log(highScores);`,
            validate: (c) => c.includes('.filter(') && c.includes('> 50') && c.includes('console.log('),
            successMsg: `Data filtered cleanly!`,
            errorMsg: `Did you use scores.filter(s => s > 50)?`
          },
          {
            id: 'js-l10', title: 'Array Reduce',
            theory: `**.reduce()** is the ultimate array method. It takes an array and "reduces" it down to a single value, like taking an array of prices and getting the total sum.\n\nIt takes an accumulator (the running total) and the current item.`,
            instructions: `Create a const 'sum' equal to nums.reduce((acc, curr) => acc + curr, 0). Print 'sum'.`,
            initialCode: `const nums = [10, 20, 30];\n// Reduce below\n`,
            solution: `const sum = nums.reduce((acc, curr) => acc + curr, 0);\nconsole.log(sum);`,
            validate: (c) => c.includes('.reduce(') && c.includes('acc + curr') && c.includes(', 0)'),
            successMsg: `Reduce mastered! You have conquered JS arrays.`,
            errorMsg: `Did you use nums.reduce((acc, curr) => acc + curr, 0)?`
          }
        ]
      }
    ]
  },

  typescript: {
    id: 'typescript', name: 'TypeScript', icon: '<i class="fa-solid fa-file-code text-blue-500"></i>', ext: 'ts',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'ts-l1', title: 'Strict Types',
            theory: `TypeScript was created by Microsoft to solve JS's dynamic bugs. It forces you to define data types strictly. Before the code runs, the TS compiler checks everything and throws an error if you mess up types.\n\nYou declare the type after a variable name using a colon (**:**).`,
            instructions: `Create a variable named 'age', strictly type it as a 'number', and set it to 25. Print it.`,
            initialCode: `// Create typed age variable below\n\n// Print age below\n`,
            solution: `let age: number = 25;\nconsole.log(age);`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('letage:number=25') && c.replace(/\s/g, '').toLowerCase().includes('console.log(age)'),
            successMsg: `Awesome! You typed your first TS variable.`,
            errorMsg: `Did you use 'let age: number = 25;'?`
          },
          {
            id: 'ts-l2', title: 'Interfaces',
            theory: `For complex objects (like a User with a name and email), you use **Interfaces** to define the exact shape of the data. If a developer forgets a field, TS blocks the code from compiling.`,
            instructions: `Create an interface named 'User'. Inside it, define a 'name' property of type 'string', and an 'age' property of type 'number'.`,
            initialCode: `// Define interface below\n`,
            solution: `interface User {\n  name: string;\n  age: number;\n}`,
            validate: (c) => c.includes('interface User') && c.includes('name: string') && c.includes('age: number'),
            successMsg: `Data structures secured! Interfaces are the backbone of TypeScript.`,
            errorMsg: `Did you write 'interface User { name: string; age: number; }'?`
          }
        ]
      },
      {
        level: 'Level 2: Advanced Types',
        lessons: [
          {
            id: 'ts-l3', title: 'Enums',
            theory: `**Enums** allow you to define a set of named constants. This makes it easier to document intent, or create a set of distinct cases (like player directions: North, South, East, West).`,
            instructions: `Create an enum named 'Direction' with the values 'Up', 'Down', 'Left', 'Right'.`,
            initialCode: `// Define enum below\n`,
            solution: `enum Direction {\n  Up,\n  Down,\n  Left,\n  Right\n}`,
            validate: (c) => c.includes('enum Direction') && c.includes('Up') && c.includes('Down'),
            successMsg: `Enum established! Your constants are safe.`,
            errorMsg: `Did you write 'enum Direction { Up, Down, Left, Right }'?`
          },
          {
            id: 'ts-l4', title: 'Union Types',
            theory: `Sometimes a variable might legitimately be more than one type. For example, a function might accept a user's ID as either a number (123) OR a string ("uuid-123"). You use the **Union operator (|)** for this.`,
            instructions: `Create a let variable named 'id' that is typed as 'string | number', and set it to 123.`,
            initialCode: `// Create union variable below\n`,
            solution: `let id: string | number = 123;`,
            validate: (c) => c.replace(/\s/g, '').includes('letid:string|number=123;') || c.replace(/\s/g, '').includes('letid:number|string=123;'),
            successMsg: `Unions mastered! You have flexible, safe types.`,
            errorMsg: `Did you use 'let id: string | number = 123;'?`
          }
        ]
      },
      {
        level: 'Level 3: Functions & Classes',
        lessons: [
          {
            id: 'ts-l5', title: 'Typed Functions',
            theory: `In TypeScript, you must type both the parameters going INTO a function, AND the return value coming OUT of the function.`,
            instructions: `Create a function 'add(a: number, b: number): number'. It should return a + b.`,
            initialCode: `// Write typed function below\n`,
            solution: `function add(a: number, b: number): number {\n  return a + b;\n}`,
            validate: (c) => c.includes('a: number') && c.includes('): number') && c.includes('return a + b'),
            successMsg: `Function typed securely!`,
            errorMsg: `Did you specify types for a, b, and the return value?`
          },
          {
            id: 'ts-l6', title: 'Access Modifiers',
            theory: `TS adds OOP features to classes, like **public**, **private**, and **protected**. If a property is private, it cannot be read or modified from outside the class instance.`,
            instructions: `Create a class 'Bank'. Inside, define a 'private' property 'balance' of type 'number' set to 100.`,
            initialCode: `// Define class below\n`,
            solution: `class Bank {\n  private balance: number = 100;\n}`,
            validate: (c) => c.includes('class Bank') && c.includes('private balance: number = 100'),
            successMsg: `Encapsulation achieved! Data is locked down.`,
            errorMsg: `Did you use 'private balance: number = 100;'?`
          }
        ]
      },
      {
        level: 'Level 4: Type Manipulation',
        lessons: [
          {
            id: 'ts-l7', title: 'Type Aliases',
            theory: `While Interfaces deal with Objects, **Type Aliases** let you create custom names for ANY type, including unions or primitives.`,
            instructions: `Create a 'type' named 'Point' that equals an object shape with 'x: number' and 'y: number'.`,
            initialCode: `// Define type alias below\n`,
            solution: `type Point = {\n  x: number;\n  y: number;\n};`,
            validate: (c) => c.includes('type Point =') && c.includes('x: number') && c.includes('y: number'),
            successMsg: `Aliases created! Great for organizing complex unions.`,
            errorMsg: `Did you use 'type Point = { x: number; y: number; }'?`
          },
          {
            id: 'ts-l8', title: 'Generics',
            theory: `**Generics** allow you to pass a "Type" as a parameter. They act like a placeholder variable (usually written as **<T>**) that locks in the exact type when the function is finally called.`,
            instructions: `Write an arrow function 'identity' with generic type <T>. It accepts '(arg: T): T' and returns 'arg'.`,
            initialCode: `// Write generic function below\n`,
            solution: `const identity = <T>(arg: T): T => {\n  return arg;\n};`,
            validate: (c) => c.includes('<T>') && c.includes('(arg: T)') && c.includes('return arg'),
            successMsg: `Generics unlocked! You are writing highly reusable, bulletproof code.`,
            errorMsg: `Did you write 'const identity = <T>(arg: T): T => { return arg; }'?`
          }
        ]
      },
      {
        level: 'Level 5: Utility Types',
        lessons: [
          {
            id: 'ts-l9', title: 'Partial',
            theory: `TypeScript provides built-in utilities to transform types. **Partial<T>** takes an existing interface and makes every single field in it optional (appends a ?). Perfect for Update APIs!`,
            instructions: `You have a User interface. Create a new type alias 'UpdateUser' that equals Partial<User>.`,
            initialCode: `interface User {\n  id: number;\n  name: string;\n}\n// Create UpdateUser type below\n`,
            solution: `type UpdateUser = Partial<User>;`,
            validate: (c) => c.replace(/\s/g, '').includes('typeUpdateUser=Partial<User>;'),
            successMsg: `Expert mode! You are manipulating types programmatically.`,
            errorMsg: `Make sure you use 'type UpdateUser = Partial<User>;'`
          },
          {
            id: 'ts-l10', title: 'Omit',
            theory: `The **Omit<T, K>** utility creates a new type by picking an existing interface, and stripping away specific keys. Perfect for stripping passwords out of user objects!`,
            instructions: `Create a type 'PublicUser' that equals Omit<User, "password">.`,
            initialCode: `interface User {\n  id: number;\n  password: string;\n}\n// Create PublicUser type below\n`,
            solution: `type PublicUser = Omit<User, "password">;`,
            validate: (c) => c.replace(/\s/g, '').includes('typePublicUser=Omit<User,"password">;'),
            successMsg: `Omit mastered! Your types are perfectly modular.`,
            errorMsg: `Did you use 'Omit<User, "password">'?`
          }
        ]
      }
    ]
  },

  cpp: {
    id: 'cpp', name: 'C++', icon: '<i class="fa-solid fa-terminal text-slate-400"></i>', ext: 'cpp',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'cpp-l1', title: 'Hello World',
            theory: `C++ is a heavy-duty, Compiled language. The compiler translates code to machine language (1s and 0s) before running, making it incredibly fast.\n\nSetup requires boilerplate:\n1. **#include &lt;iostream&gt;** imports the I/O library.\n2. **int main() { }** is the absolute entry point.\n3. **std::cout &lt;&lt;** is used to print.\n4. Every statement MUST end with a semicolon (**;**).`,
            instructions: `Inside main(), use std::cout << to print "Hello World", followed by a semicolon.`,
            initialCode: `#include <iostream>\n\nint main() {\n    // Write code below\n    \n    return 0;\n}`,
            solution: `#include <iostream>\nint main() {\n    std::cout << "Hello World";\n    return 0;\n}`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('std::cout<<"helloworld"') || c.replace(/\s/g, '').toLowerCase().includes('std::cout<<"helloworld!"'),
            successMsg: `Incredible! C++ syntax is tough, but you nailed it.`,
            errorMsg: `Did you use std::cout << "Hello World"; ? Don't forget the semicolon!`
          },
          {
            id: 'cpp-l2', title: 'Strong Typing',
            theory: `C++ uses **Strong Static Typing**. You MUST explicitly tell the computer what kind of data a variable holds. The compiler uses this to reserve physical RAM bytes.\n\n**Common Types:**\n**int**: Whole numbers (4 bytes)\n**float**: Decimals (4 bytes)\n**std::string**: Text`,
            instructions: `Inside main, create an 'int' named 'ammo' set to 30. On the next line, print it using std::cout. Remember your semicolons!`,
            initialCode: `#include <iostream>\n\nint main() {\n    // Create int ammo here\n    \n    // Print ammo here\n    \n    return 0;\n}`,
            solution: `int ammo = 30;\nstd::cout << ammo;`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('intammo=30;') && c.replace(/\s/g, '').toLowerCase().includes('std::cout<<ammo;'),
            successMsg: `Strong typing mastered. You are on your way!`,
            errorMsg: `Make sure to declare 'int ammo = 30;' and 'std::cout << ammo;' with semicolons.`
          }
        ]
      },
      {
        level: 'Level 2: Memory Mastery',
        lessons: [
          {
            id: 'cpp-l3', title: 'Raw Pointers',
            theory: `A **Pointer** (*) is a special variable that doesn't hold data; it holds the physical hexadecimal memory address of another variable. You get the memory address using the ampersand (&). \n\nExample: 'int* ptr = &health;'`,
            instructions: `You have an int called 'score'. Create an integer pointer 'ptr' (int*) and set it to the address of score (&score).`,
            initialCode: `int main() {\n    int score = 500;\n    // Create pointer below\n    \n    return 0;\n}`,
            solution: `int* ptr = &score;`,
            validate: (c) => c.replace(/\s/g, '').includes('int*ptr=&score;'),
            successMsg: `Welcome to the Matrix! You are manipulating raw RAM.`,
            errorMsg: `Did you write 'int* ptr = &score;' ? Don't forget the semicolon!`
          },
          {
            id: 'cpp-l4', title: 'The Heap',
            theory: `C++ has NO garbage collector. When you allocate memory dynamically on the "Heap" using the **new** keyword, you MUST manually destroy it using **delete** when finished. Forgetting causes a "Memory Leak" that crashes the computer.`,
            instructions: `Create an int pointer 'ptr' and allocate heap memory using 'new int(10)'. On the next line, destroy it using 'delete ptr;'.`,
            initialCode: `int main() {\n    // Allocate heap memory\n    \n    // Delete it immediately\n    \n    return 0;\n}`,
            solution: `int* ptr = new int(10);\ndelete ptr;`,
            validate: (c) => c.includes('new int') && c.includes('delete ptr;'),
            successMsg: `Crisis averted! You successfully managed the heap.`,
            errorMsg: `Make sure you use 'new int(10)' and follow it up with 'delete ptr;'`
          }
        ]
      },
      {
        level: 'Level 3: Data Structures',
        lessons: [
          {
            id: 'cpp-l5', title: 'Vectors',
            theory: `Standard C++ arrays are fixed in size. To get flexible, growing arrays, C++ provides **std::vector** from the Standard Template Library (STL).\n\nYou add items using '.push_back()'.`,
            instructions: `Create a std::vector of ints named 'nums'. On the next line, call nums.push_back(5);`,
            initialCode: `#include <vector>\nint main() {\n    // Create vector below\n    \n    return 0;\n}`,
            solution: `std::vector<int> nums;\nnums.push_back(5);`,
            validate: (c) => c.includes('std::vector<int>') && c.includes('nums.push_back(5);'),
            successMsg: `Vectors unlocked! You are using the STL.`,
            errorMsg: `Did you declare 'std::vector<int> nums;' and push_back(5)?`
          },
          {
            id: 'cpp-l6', title: 'Structs',
            theory: `A **Struct** is a lightweight way to group variables together into a single custom data type, like grouping x, y, and z coordinates.`,
            instructions: `Define a 'struct' named 'Vector3'. Inside it, declare three public ints: x, y, and z. Don't forget the semicolon at the end of the struct block!`,
            initialCode: `// Define struct below\n`,
            solution: `struct Vector3 {\n    int x;\n    int y;\n    int z;\n};`,
            validate: (c) => c.includes('struct Vector3') && c.includes('int x;') && c.includes('};'),
            successMsg: `Custom data structures built!`,
            errorMsg: `Did you put x, y, and z inside the struct and end with }; ?`
          }
        ]
      },
      {
        level: 'Level 4: OOP Mechanics',
        lessons: [
          {
            id: 'cpp-l7', title: 'Classes',
            theory: `While Structs default to public data, **Classes** default to private data. They are the backbone of C++ Object-Oriented Programming.`,
            instructions: `Create a class 'Dog'. Use the 'public:' label. Below it, define a void method 'bark()' that prints "Woof".`,
            initialCode: `// Define class below\n`,
            solution: `class Dog {\npublic:\n    void bark() {\n        std::cout << "Woof";\n    }\n};`,
            validate: (c) => c.includes('class Dog') && c.includes('public:') && c.includes('void bark()'),
            successMsg: `OOP foundation laid!`,
            errorMsg: `Did you use the 'public:' label inside the class?`
          },
          {
            id: 'cpp-l8', title: 'Constructors',
            theory: `A **Constructor** is a special method called automatically when an object is instantiated. It has the EXACT same name as the class and no return type.`,
            instructions: `Inside class Car, write a public constructor 'Car(int s)' that sets the class variable 'speed' equal to 's'.`,
            initialCode: `class Car {\n    int speed;\npublic:\n    // Write constructor below\n    \n};`,
            solution: `Car(int s) {\n    speed = s;\n}`,
            validate: (c) => c.includes('Car(int') && c.includes('speed = '),
            successMsg: `Constructors engaged! Objects now initialize safely.`,
            errorMsg: `Make sure the constructor is named 'Car' and sets speed.`
          }
        ]
      },
      {
        level: 'Level 5: Modern C++',
        lessons: [
          {
            id: 'cpp-l9', title: 'Auto Keyword',
            theory: `C++11 introduced the **auto** keyword. It allows the compiler to deduce the type of a variable automatically, saving you from typing horrific, long iterator types!`,
            instructions: `Create a variable named 'score' using the 'auto' keyword, and set it to 100.`,
            initialCode: `int main() {\n    // Use auto below\n    \n    return 0;\n}`,
            solution: `auto score = 100;`,
            validate: (c) => c.includes('auto score = 100;'),
            successMsg: `Auto makes modern C++ so much cleaner!`,
            errorMsg: `Did you use 'auto score = 100;'?`
          },
          {
            id: 'cpp-l10', title: 'References (&)',
            theory: `Passing massive objects to functions copies them, wasting CPU. Pointers avoid copies but are dangerous. **References (&)** act like safer, non-null pointers that alias an existing variable.`,
            instructions: `You have an int 'health'. Create an int reference named 'ref' (int&) and set it equal to health.`,
            initialCode: `int main() {\n    int health = 100;\n    // Create reference below\n    \n    return 0;\n}`,
            solution: `int& ref = health;`,
            validate: (c) => c.replace(/\s/g, '').includes('int&ref=health;'),
            successMsg: `References mastered! Your functions will be incredibly fast.`,
            errorMsg: `Did you use 'int& ref = health;'?`
          }
        ]
      }
    ]
  },

  csharp: {
    id: 'csharp', name: 'C#', icon: '<i class="fa-solid fa-hashtag text-purple-400"></i>', ext: 'cs',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'cs-l1', title: 'Hello World',
            theory: `C# (pronounced "C-Sharp") is heavily structured. It is massively popular in enterprise web services (.NET) and the **Unity Game Engine**.\n\nTo print messages, C# uses a method called **Console.WriteLine()**. Statements must terminate with a semicolon (**;**).`,
            instructions: `Inside Main(), use Console.WriteLine() to print "Hello World".`,
            initialCode: `using System;\nclass Program {\n    static void Main() {\n        // Write code below\n        \n    }\n}`,
            solution: `Console.WriteLine("Hello World");`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('console.writeline("helloworld'),
            successMsg: `Awesome! You wrote your first C# program.`,
            errorMsg: `Make sure you use Console.WriteLine()!`
          },
          {
            id: 'cs-l2', title: 'Variables',
            theory: `C# is strongly typed. Notice that the word 'string' has a lowercase 's' in C#, which is different from Java! \n\n**Examples:**\nstring name = "Alice";\nint health = 100;\nbool isAlive = true;`,
            instructions: `Inside Main, create an 'int' named 'age' and set it to 25. Print it using Console.WriteLine().`,
            initialCode: `using System;\nclass Program {\n    static void Main() {\n        // Create int age\n        \n        // Print it\n        \n    }\n}`,
            solution: `int age = 25;\nConsole.WriteLine(age);`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('intage=25;') && c.replace(/\s/g, '').toLowerCase().includes('console.writeline(age)'),
            successMsg: `Perfect! C# typing mastered.`,
            errorMsg: `Did you use 'int age = 25;' and 'Console.WriteLine(age);'?`
          }
        ]
      },
      {
        level: 'Level 2: Enterprise OOP',
        lessons: [
          {
            id: 'cs-l3', title: 'Properties (Get/Set)',
            theory: `We use **Properties** to protect data. Instead of writing GetHealth() and SetHealth() methods, C# has a beautiful shorthand syntax: 'public int Health { get; set; }'.`,
            instructions: `Inside Player, create a public string property named 'Name' with an auto-implemented { get; set; }.`,
            initialCode: `class Player {\n    // Create property below\n    \n}`,
            solution: `public string Name { get; set; }`,
            validate: (c) => c.includes('public string Name') && c.includes('{') && c.includes('get;') && c.includes('set;'),
            successMsg: `Excellent! Auto-properties are universally used in C#.`,
            errorMsg: `Did you write 'public string Name { get; set; }'? Watch capitalization!`
          },
          {
            id: 'cs-l4', title: 'Methods',
            theory: `Methods are functions attached to classes. By convention, C# method names start with a Capital letter (PascalCase).`,
            instructions: `Inside class MathTool, create a public method 'Add' that takes (int a, int b) and returns an int. Return a + b.`,
            initialCode: `class MathTool {\n    // Create Add method below\n    \n}`,
            solution: `public int Add(int a, int b) {\n    return a + b;\n}`,
            validate: (c) => c.includes('public int Add') && c.includes('return a + b;'),
            successMsg: `Methods constructed properly!`,
            errorMsg: `Did you name it Add and return an int?`
          }
        ]
      },
      {
        level: 'Level 3: Collections',
        lessons: [
          {
            id: 'cs-l5', title: 'Lists',
            theory: `Standard arrays 'int[]' are rigid. C# uses **List&lt;T&gt;** for flexible collections that can grow. You initialize them with the 'new' keyword.`,
            instructions: `Create a List of ints named 'scores' equal to 'new List<int>()'. Then call scores.Add(100);`,
            initialCode: `using System.Collections.Generic;\nclass Program {\n    static void Main() {\n        // Create List below\n        \n    }\n}`,
            solution: `List<int> scores = new List<int>();\nscores.Add(100);`,
            validate: (c) => c.includes('List<int>') && c.includes('new List<int>()') && c.includes('.Add(100)'),
            successMsg: `Generic Lists are the core of C# collections!`,
            errorMsg: `Did you instantiate with new List<int>() and Add 100?`
          },
          {
            id: 'cs-l6', title: 'Dictionaries',
            theory: `**Dictionary&lt;TKey, TValue&gt;** maps keys to values for lightning-fast lookups, identical to HashMaps in Java or dicts in Python.`,
            instructions: `Create a Dictionary mapping string to int named 'ages' equal to 'new Dictionary<string, int>()'.`,
            initialCode: `using System.Collections.Generic;\nclass Program {\n    static void Main() {\n        // Create Dictionary below\n        \n    }\n}`,
            solution: `Dictionary<string, int> ages = new Dictionary<string, int>();`,
            validate: (c) => c.includes('Dictionary<string, int>') && c.includes('new Dictionary'),
            successMsg: `Dictionaries ready! Great for IDs and values.`,
            errorMsg: `Check your generic types: <string, int>`
          }
        ]
      },
      {
        level: 'Level 4: LINQ',
        lessons: [
          {
            id: 'cs-l7', title: 'LINQ Where',
            theory: `**Language Integrated Query (LINQ)** allows you to write elegant, database-like queries directly in C# using extension methods like '.Where()'.`,
            instructions: `You have an array of 'scores'. Create a var 'high' set to scores.Where(s => s > 100).`,
            initialCode: `using System.Linq;\nclass Program {\n    static void Main() {\n        int[] scores = { 50, 150, 80 };\n        // Write LINQ below\n        \n    }\n}`,
            solution: `var high = scores.Where(s => s > 100);`,
            validate: (c) => c.includes('scores.Where(') && c.includes('> 100'),
            successMsg: `LINQ Mastered! You filtered data effortlessly.`,
            errorMsg: `Make sure you call 'scores.Where(s => s > 100)'!`
          },
          {
            id: 'cs-l8', title: 'LINQ Select',
            theory: `The **.Select()** LINQ method transforms data, exactly like .map() in JavaScript. It projects each element into a new form.`,
            instructions: `Use scores.Select(s => s * 2) to double the scores, and assign it to a var named 'doubled'.`,
            initialCode: `using System.Linq;\nclass Program {\n    static void Main() {\n        int[] scores = { 10, 20, 30 };\n        // Select below\n        \n    }\n}`,
            solution: `var doubled = scores.Select(s => s * 2);`,
            validate: (c) => c.includes('.Select(') && c.includes('* 2'),
            successMsg: `Data transformed! LINQ is incredibly powerful.`,
            errorMsg: `Did you use scores.Select(s => s * 2)?`
          }
        ]
      },
      {
        level: 'Level 5: Asynchronous',
        lessons: [
          {
            id: 'cs-l9', title: 'Tasks',
            theory: `To keep UIs from freezing, C# executes heavy work on background threads using the **Task** parallel library.`,
            instructions: `Create a 'Task' named 'work' equal to 'Task.Delay(1000)'.`,
            initialCode: `using System.Threading.Tasks;\nclass Program {\n    static void Main() {\n        // Create Task below\n        \n    }\n}`,
            solution: `Task work = Task.Delay(1000);`,
            validate: (c) => c.includes('Task ') && c.includes('Task.Delay(1000)'),
            successMsg: `Thread scheduled!`,
            errorMsg: `Did you assign Task.Delay to a Task variable?`
          },
          {
            id: 'cs-l10', title: 'Async/Await',
            theory: `You consume Tasks elegantly using the **async** and **await** keywords. The method signature must return a Task.`,
            instructions: `Create a 'public async Task GetData()' method. Inside, simply 'await Task.Delay(1000);'.`,
            initialCode: `using System.Threading.Tasks;\nclass Api {\n    // Write async method below\n    \n}`,
            solution: `public async Task GetData() {\n    await Task.Delay(1000);\n}`,
            validate: (c) => c.includes('async Task') && c.includes('await Task.Delay'),
            successMsg: `Asynchronous .NET mastered!`,
            errorMsg: `Ensure the signature is 'public async Task GetData()'.`
          }
        ]
      }
    ]
  },

  java: {
    id: 'java', name: 'Java', icon: '<i class="fa-brands fa-java text-orange-400 text-lg"></i>', ext: 'java',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'java-l1', title: 'Hello World',
            theory: `Java enforces strict Object-Oriented design. Absolutely everything you write MUST exist inside a "class".\n\nTo print output, we trace through Java's system packages using **System.out.println()**.`,
            instructions: `Inside main, use System.out.println() to print "Hello World". Don't forget the semicolon!`,
            initialCode: `class Main {\n    public static void main(String[] args) {\n        // Write code below\n        \n    }\n}`,
            solution: `System.out.println("Hello World");`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('system.out.println("helloworld'),
            successMsg: `Awesome! You wrote your first Java program.`,
            errorMsg: `Make sure you use System.out.println()!`
          },
          {
            id: 'java-l2', title: 'Static Typing',
            theory: `Java uses strict static typing. The Java compiler is notorious for being extremely strict, which prevents bugs in massive corporate codebases.\n\nBecause text is treated as an Object, the word **String** must be capitalized!`,
            instructions: `Inside main, create an 'int' named 'age' and set it to 25. Then print it.`,
            initialCode: `class Main {\n    public static void main(String[] args) {\n        // Create int age\n        \n        // Print it\n        \n    }\n}`,
            solution: `int age = 25;\nSystem.out.println(age);`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('intage=25;') && c.replace(/\s/g, '').toLowerCase().includes('system.out.println(age)'),
            successMsg: `Perfect! Typed variables are working correctly.`,
            errorMsg: `Did you use 'int age = 25;' and print it?`
          }
        ]
      },
      {
        level: 'Level 2: Strict OOP',
        lessons: [
          {
            id: 'java-l3', title: 'Constructors',
            theory: `To instantiate an Object (like a new Car), you initialize its data using a **Constructor**. It has the EXACT same name as the class.`,
            instructions: `Inside 'Dog', create a public constructor 'Dog' taking a String 'n'. Set the class variable 'name' equal to 'n'.`,
            initialCode: `class Dog {\n    String name;\n    // Write constructor below\n    \n}`,
            solution: `public Dog(String n) {\n    name = n;\n}`,
            validate: (c) => c.includes('Dog(String') && c.includes('name = '),
            successMsg: `Constructor built! You can now instantiate objects.`,
            errorMsg: `Did you write 'public Dog(String n) { name = n; }'?`
          },
          {
            id: 'java-l4', title: 'Encapsulation',
            theory: `Java strictly uses Encapsulation. Variables are marked **private**, and you expose them safely using public Getter and Setter methods.`,
            instructions: `Create a public method 'getScore()' that returns the private 'score' variable.`,
            initialCode: `class Player {\n    private int score = 100;\n    // Write getScore method below\n    \n}`,
            solution: `public int getScore() {\n    return score;\n}`,
            validate: (c) => c.includes('public int getScore()') && c.includes('return score;'),
            successMsg: `Getters and Setters are standard Java practice.`,
            errorMsg: `Did you return an int from getScore()?`
          }
        ]
      },
      {
        level: 'Level 3: Collections',
        lessons: [
          {
            id: 'java-l5', title: 'ArrayLists',
            theory: `Standard arrays are rigidly fixed in size. The **ArrayList** acts like a standard list but expands automatically via '.add()'.`,
            instructions: `Create an ArrayList of Strings named 'list' and initialize it with 'new ArrayList<>()'. On the next line, call list.add("Apple");.`,
            initialCode: `import java.util.ArrayList;\nclass Main {\n    public static void main(String[] args) {\n        // Create ArrayList below\n        \n    }\n}`,
            solution: `ArrayList<String> list = new ArrayList<>();\nlist.add("Apple");`,
            validate: (c) => c.replace(/\s/g, '').includes('ArrayList<String>list=newArrayList') && c.includes('.add("Apple");'),
            successMsg: `Collections mastered! You've broken free from rigid arrays.`,
            errorMsg: `Did you write 'ArrayList<String> list = new ArrayList<>();' ?`
          },
          {
            id: 'java-l6', title: 'HashMaps',
            theory: `A **HashMap** stores objects in Key-Value pairs. It requires two Generic types, one for the key, and one for the value.`,
            instructions: `Create a HashMap mapping String to Integer named 'map' equal to 'new HashMap<>()'.`,
            initialCode: `import java.util.HashMap;\nclass Main {\n    public static void main(String[] args) {\n        // Create HashMap below\n        \n    }\n}`,
            solution: `HashMap<String, Integer> map = new HashMap<>();`,
            validate: (c) => c.replace(/\s/g, '').includes('HashMap<String,Integer>map=newHashMap'),
            successMsg: `Key-Value pairs established.`,
            errorMsg: `Did you define the generic types <String, Integer>?`
          }
        ]
      },
      {
        level: 'Level 4: Advanced OOP',
        lessons: [
          {
            id: 'java-l7', title: 'Interfaces',
            theory: `A Java **Interface** is a 100% abstract contract. Any class that 'implements' the interface MUST write the code for its methods.`,
            instructions: `Define an interface 'Animal'. Inside it, declare a void method 'makeSound();' (no braces!).`,
            initialCode: `// Define interface below\n`,
            solution: `interface Animal {\n    void makeSound();\n}`,
            validate: (c) => c.includes('interface Animal') && c.includes('void makeSound();'),
            successMsg: `Contract established! Polymorphism awaits.`,
            errorMsg: `Make sure you declare the method without a body (no {}).`
          },
          {
            id: 'java-l8', title: 'Inheritance',
            theory: `Classes can inherit properties from a parent class using the **extends** keyword.`,
            instructions: `Create a class 'Car' that 'extends Vehicle'.`,
            initialCode: `class Vehicle {}\n// Extend Vehicle below\n`,
            solution: `class Car extends Vehicle {}`,
            validate: (c) => c.includes('class Car extends Vehicle'),
            successMsg: `Class hierarchy created!`,
            errorMsg: `Did you use 'class Car extends Vehicle'?`
          }
        ]
      },
      {
        level: 'Level 5: Robustness',
        lessons: [
          {
            id: 'java-l9', title: 'Exceptions',
            theory: `Java requires you to catch errors using **try / catch** blocks. The catch block requires an Exception type.`,
            instructions: `Write a try block doing 'int x = 1/0;'. Follow it with a 'catch (Exception e)' block that prints "Error".`,
            initialCode: `class Main {\n    public static void main(String[] args) {\n        // Write try/catch below\n        \n    }\n}`,
            solution: `try {\n    int x = 1/0;\n} catch (Exception e) {\n    System.out.println("Error");\n}`,
            validate: (c) => c.includes('try {') && c.includes('catch (Exception') && c.includes('System.out.println'),
            successMsg: `Exceptions caught successfully.`,
            errorMsg: `Did you use 'catch (Exception e)'?`
          },
          {
            id: 'java-l10', title: 'For-Each Loops',
            theory: `Iterating over collections safely is best done with an enhanced **for-each** loop rather than index counters.`,
            instructions: `Given array 'names', write a loop: 'for (String n : names)'. Inside, print 'n'.`,
            initialCode: `class Main {\n    public static void main(String[] args) {\n        String[] names = {"Bob", "Sue"};\n        // Write for-each below\n        \n    }\n}`,
            solution: `for (String n : names) {\n    System.out.println(n);\n}`,
            validate: (c) => c.includes('for (String ') && c.includes(': names)') && c.includes('println('),
            successMsg: `Clean iterations achieved!`,
            errorMsg: `Did you use the enhanced for (String n : names) loop?`
          }
        ]
      }
    ]
  },

  lua: {
    id: 'lua', name: 'Lua', icon: '<i class="fa-solid fa-moon text-indigo-400"></i>', ext: 'lua',
    levels: [
      {
        level: 'Level 1: Fundamentals',
        lessons: [
          {
            id: 'lua-l1', title: 'Hello World',
            theory: `Lua is a remarkably lightweight, lightning-fast scripting language explicitly designed to be embedded inside massive game engines (Roblox, WoW, LÖVE2D).\n\nIt uses the **print()** function to display messages. Semicolons are optional.`,
            instructions: `Use the print function to output "Hello World" to the console.`,
            initialCode: `-- Write your code below\n`,
            solution: `print("Hello World")`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('print("helloworld")') || c.replace(/\s/g, '').toLowerCase().includes("print('helloworld')"),
            successMsg: `Great job! You've conquered Lua's syntax.`,
            errorMsg: `Check your syntax. Did you type print("Hello World")?`
          },
          {
            id: 'lua-l2', title: 'Local Variables',
            theory: `In Lua, it is a strict best practice to define variables using the **local** keyword. If you forget 'local', the variable becomes "global", meaning every single other script running in your entire game engine can accidentally overwrite it!\n\n**Example:**\nlocal health = 100`,
            instructions: `Create a local variable named 'score' and set it to 100. On the next line, print it.`,
            initialCode: `-- Create local variable below\n\n-- Print it below\n`,
            solution: `local score = 100\nprint(score)`,
            validate: (c) => c.replace(/\s/g, '').toLowerCase().includes('localscore=100') && c.replace(/\s/g, '').toLowerCase().includes('print(score)'),
            successMsg: `Excellent! Always remember your 'local' keywords in Lua.`,
            errorMsg: `Did you use 'local score = 100' and 'print(score)'?`
          }
        ]
      },
      {
        level: 'Level 2: Engine Scripting',
        lessons: [
          {
            id: 'lua-l3', title: 'Tables',
            theory: `Lua has ONE complex data structure: a **Table**. It acts as an Array, Dictionary, and Object all at the same time. Lua tables start indexing at **1**!\n\nYou use curly braces {} to create them.`,
            instructions: `Create a local variable 'inventory' set to a table containing "Sword" and "Shield".`,
            initialCode: `-- Create table below\n`,
            solution: `local inventory = {"Sword", "Shield"}`,
            validate: (c) => c.includes('local inventory') && c.includes('{') && c.includes('Sword'),
            successMsg: `Tables unlocked! This is the core of Lua programming.`,
            errorMsg: `Did you create 'local inventory = {"Sword", "Shield"}'?`
          },
          {
            id: 'lua-l4', title: 'Iterating Pairs',
            theory: `We iterate tables using a generic 'for' loop paired with the built-in **ipairs()** (for arrays) or **pairs()** (for dictionaries) functions.`,
            instructions: `Write a loop: 'for index, item in ipairs(inventory) do'. Inside, 'print(item)'. Don't forget 'end'!`,
            initialCode: `local inventory = {"Sword", "Bow"}\n-- Write loop below\n`,
            solution: `for index, item in ipairs(inventory) do\n    print(item)\nend`,
            validate: (c) => c.includes('for ') && c.includes('ipairs') && c.includes('print(') && c.includes('end'),
            successMsg: `Loops mastered! Required for almost all game logic.`,
            errorMsg: `Did you close the loop with 'end'?`
          }
        ]
      },
      {
        level: 'Level 3: Functions',
        lessons: [
          {
            id: 'lua-l5', title: 'Anonymous Functions',
            theory: `Functions in Lua are "first-class citizens". You can assign them to variables, just like numbers or strings, without giving them a standard name.`,
            instructions: `Create a 'local' variable 'sayHi' and set it to 'function() print("Hi") end'.`,
            initialCode: `-- Assign function to variable below\n`,
            solution: `local sayHi = function()\n    print("Hi")\nend`,
            validate: (c) => c.includes('local sayHi = function()') && c.includes('print("Hi")') && c.includes('end'),
            successMsg: `First class functions are powerful for engine callbacks.`,
            errorMsg: `Did you assign function() to a local variable?`
          },
          {
            id: 'lua-l6', title: 'Table Functions',
            theory: `Since tables can hold anything, they can hold functions! This is how you build Modules and Objects in Lua.`,
            instructions: `You have a table 'Player'. Add a property 'attack' equal to 'function() print("Hit") end'.`,
            initialCode: `local Player = {}\n-- Add function to table below\n`,
            solution: `Player.attack = function()\n    print("Hit")\nend`,
            validate: (c) => c.includes('Player.attack = function()') && c.includes('print('),
            successMsg: `Methods added to tables! This simulates OOP.`,
            errorMsg: `Did you assign a function to Player.attack?`
          }
        ]
      },
      {
        level: 'Level 4: Metatables',
        lessons: [
          {
            id: 'lua-l7', title: 'The __index Metamethod',
            theory: `**Metatables** modify how tables behave. The '__index' metamethod fires when you ask a table for a key it doesn't have. It acts as a "fallback", which is how Inheritance works in Lua!`,
            instructions: `Create a table 'meta'. Inside, set '__index = function() return "Unknown" end'.`,
            initialCode: `-- Create meta table below\n`,
            solution: `local meta = {\n    __index = function()\n        return "Unknown"\n    end\n}`,
            validate: (c) => c.includes('__index') && c.includes('return "Unknown"'),
            successMsg: `Metamethods are the deepest secret of Lua!`,
            errorMsg: `Did you define the __index function?`
          },
          {
            id: 'lua-l8', title: 'Operator Overloading',
            theory: `You can use metatables to define how mathematical operators (+, -, *, /) work on your custom tables using metamethods like '__add'.`,
            instructions: `Set the '__add' metamethod in 'meta' to 'function(a, b) return a.value + b.value end'.`,
            initialCode: `local meta = {}\n-- Define __add below\n`,
            solution: `meta.__add = function(a, b)\n    return a.value + b.value\nend`,
            validate: (c) => c.includes('__add') && c.includes('a.value + b.value'),
            successMsg: `You just overloaded math operators!`,
            errorMsg: `Did you define meta.__add correctly?`
          }
        ]
      },
      {
        level: 'Level 5: Standard Libraries',
        lessons: [
          {
            id: 'lua-l9', title: 'String Manipulation',
            theory: `Lua has a powerful built-in 'string' library. You can find substrings using 'string.find' or make strings uppercase using 'string.upper'.`,
            instructions: `Create a local variable 'yell' set to 'string.upper("hello")'. Print 'yell'.`,
            initialCode: `-- Use string library below\n`,
            solution: `local yell = string.upper("hello")\nprint(yell)`,
            validate: (c) => c.includes('string.upper') && c.includes('print(yell)'),
            successMsg: `String library utilized successfully!`,
            errorMsg: `Did you call string.upper("hello")?`
          },
          {
            id: 'lua-l10', title: 'Math Module',
            theory: `For game engines, the 'math' library is essential. It provides 'math.random', 'math.floor', 'math.abs', and more.`,
            instructions: `Create a local variable 'roll' set to 'math.random(1, 6)'. Print 'roll'.`,
            initialCode: `-- Use math library below\n`,
            solution: `local roll = math.random(1, 6)\nprint(roll)`,
            validate: (c) => c.includes('math.random(1, 6)') && c.includes('print(roll)'),
            successMsg: `RNG constructed! You are ready to build games.`,
            errorMsg: `Did you call math.random(1, 6)?`
          }
        ]
      }
    ]
  }
};

// ==========================================
// 2. STATE MANAGEMENT
// ==========================================
const appState = {
  activeLang: 'python',
  activeLessonId: 'py-l1',
  codeData: {},
  completed: {},
  terminal: { status: 'idle', msg: 'Awaiting execution...' }
};

// ==========================================
// 3. DOM ELEMENT CACHING
// ==========================================
const DOM = {
  navTabs: document.getElementById('nav-tabs'),
  sidebar: document.getElementById('sidebar'),
  sidebarToggle: document.getElementById('sidebar-toggle'),
  sidebarTitle: document.getElementById('sidebar-title'),
  sidebarContent: document.getElementById('sidebar-content'),
  mainWorkspace: document.getElementById('main-workspace'),
  lessonContent: document.getElementById('lesson-content'),
  editorTab: document.getElementById('editor-tab'),
  editorActions: document.getElementById('editor-actions'),
  codeEditor: document.getElementById('code-editor'),
  terminalOutput: document.getElementById('terminal-output')
};

// ==========================================
// 4. HELPERS
// ==========================================
const getActiveLangObj = () => languagesData[appState.activeLang];

const getAllLessonIds = () => {
  return getActiveLangObj().levels.flatMap(lvl => lvl.lessons ? lvl.lessons.map(l => l.id) : []);
};

const getActiveLessonObj = () => {
  const allLessons = getActiveLangObj().levels.flatMap(lvl => lvl.lessons || []);
  return allLessons.find(l => l.id === appState.activeLessonId) || null;
};

const isSkippingAhead = () => {
  const ids = getAllLessonIds();
  const currentIndex = ids.indexOf(appState.activeLessonId);
  for (let i = 0; i < currentIndex; i++) {
    if (!appState.completed[ids[i]]) return true;
  }
  return false;
};

const formatTheoryText = (text) => {
  return text.split('\n').map(line => {
    if (!line) return '<br />';
    const boldParsed = line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-zinc-100 font-semibold">$1</strong>');
    return `<p class="mb-3">${boldParsed}</p>`;
  }).join('');
};

// ==========================================
// 5. RENDERERS
// ==========================================
const renderViews = () => {
  const lang = getActiveLangObj();
  const lesson = getActiveLessonObj();
  const allIds = getAllLessonIds();
  const currentIndex = allIds.indexOf(appState.activeLessonId);
  const nextLessonId = currentIndex < allIds.length - 1 ? allIds[currentIndex + 1] : null;

  // 5A: Render Top Navigation Tabs
  DOM.navTabs.innerHTML = Object.values(languagesData).map(l => {
    const isActive = appState.activeLang === l.id;
    const classes = isActive
      ? 'border-blue-500 text-white bg-zinc-800/50'
      : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/30';
    return `
      <button data-action="set-lang" data-id="${l.id}" class="h-full px-4 flex items-center gap-2 text-sm font-medium transition-colors border-b-2 ${classes}">
        ${l.icon} ${l.name}
      </button>
    `;
  }).join('');

  // 5B: Render Sidebar Curriculum
  DOM.sidebarTitle.innerHTML = `${lang.name} Curriculum`;
  DOM.sidebarContent.innerHTML = lang.levels.map(lvl => `
    <div>
      <h4 class="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-2 px-2 flex items-center gap-2">${lvl.level}</h4>
      ${lvl.lessons ? `<div class="space-y-0.5">
        ${lvl.lessons.map(l => {
          const isCompleted = appState.completed[l.id];
          const isActive = appState.activeLessonId === l.id;
          const btnClasses = isActive ? 'bg-blue-500/10 text-blue-400 font-medium' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200';
          const iconHtml = isCompleted
            ? `<i class="fa-solid fa-circle-check text-green-500/80 flex-shrink-0"></i>`
            : `<div class="w-4 h-4 rounded-full border flex-shrink-0 ${isActive ? 'border-blue-500/50' : 'border-zinc-700'}"></div>`;
          return `
            <button data-action="set-lesson" data-id="${l.id}" class="w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 text-sm transition-all duration-200 ${btnClasses}">
              ${iconHtml} <span class="truncate">${l.title}</span>
            </button>
          `;
        }).join('')}
      </div>` : ''}
    </div>
  `).join('');

  // 5C: Render Main Lesson Text
  if (!lesson) {
    DOM.lessonContent.innerHTML = `<p class="text-zinc-500">Select a lesson.</p>`;
  } else {
    DOM.lessonContent.innerHTML = `
      <div class="animate-fadeIn">
        ${isSkippingAhead() ? `
          <div class="bg-amber-500/10 border border-amber-500/20 text-amber-500 px-5 py-4 rounded-xl mb-8 flex items-center gap-3 mt-2 shadow-lg">
            <i class="fa-solid fa-triangle-exclamation text-xl flex-shrink-0"></i>
            <p class="text-sm leading-relaxed">
              <strong>You skipped ahead!</strong> We highly recommend completing previous lessons first.
            </p>
          </div>
        ` : ''}
        <h1 class="text-3xl lg:text-4xl font-extrabold text-white mb-6 tracking-tight flex items-center gap-3 mt-2">${lesson.title}</h1>
        <div class="text-zinc-400 leading-relaxed text-base mb-8">${formatTheoryText(lesson.theory)}</div>
        <div class="bg-[#121214] border border-zinc-800/80 rounded-xl p-6 mt-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1 h-full bg-blue-500/50"></div>
          <h3 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-2">
            <i class="fa-solid fa-check text-blue-400"></i> Your Task
          </h3>
          <p class="text-zinc-200 text-base">${lesson.instructions}</p>
        </div>
      </div>
    `;
  }

  // 5D: Render Editor Panel
  DOM.editorTab.innerHTML = `${lang.icon} main.${lang.ext}`;
  if (DOM.codeEditor.value !== (appState.codeData[appState.activeLessonId] || '')) {
     DOM.codeEditor.value = appState.codeData[appState.activeLessonId] || '';
  }

  let actionsHtml = '';
  if (appState.terminal.status === 'success' && nextLessonId) {
    actionsHtml += `
      <button data-action="set-lesson" data-id="${nextLessonId}" class="flex items-center gap-1.5 px-4 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-semibold rounded-md transition-all animate-pulse">
        Next Lesson <i class="fa-solid fa-chevron-right text-[10px]"></i>
      </button>
    `;
  }
  actionsHtml += `
    <button data-action="run-code" class="flex items-center gap-1.5 px-4 py-1.5 bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-bold rounded-md transition-colors shadow-sm">
      <i class="fa-solid fa-play text-[10px]"></i> Run
    </button>
  `;
  DOM.editorActions.innerHTML = actionsHtml;

  // 5E: Render Terminal
  let tHtml = '';
  if (appState.terminal.status === 'idle') tHtml = `<span class="text-zinc-600">${appState.terminal.msg}</span>`;
  else if (appState.terminal.status === 'success') tHtml = `<span class="text-emerald-400 flex items-center gap-2"><i class="fa-solid fa-circle-check"></i> ${appState.terminal.msg}</span>`;
  else if (appState.terminal.status === 'error') tHtml = `<span class="text-red-400 flex items-center gap-2"><i class="fa-solid fa-triangle-exclamation"></i> ${appState.terminal.msg}</span>`;
  DOM.terminalOutput.innerHTML = tHtml;
};

// ==========================================
// 6. CONTROLLERS & EVENT DELEGATION
// ==========================================

// Live save user code
DOM.codeEditor.addEventListener('input', (e) => {
  appState.codeData[appState.activeLessonId] = e.target.value;
});

// Sidebar Toggle
DOM.sidebarToggle.addEventListener('click', () => DOM.sidebar.classList.toggle('-ml-64'));

// Global Click Handler (Event Delegation)
document.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;

  const action = btn.dataset.action;

  if (action === 'set-lang') {
    const langId = btn.dataset.id;
    appState.activeLang = langId;
    const langConfig = getActiveLangObj();
    if (langConfig.levels[0].lessons) {
      appState.activeLessonId = langConfig.levels[0].lessons[0].id;
    }
    appState.terminal = { status: 'idle', msg: 'Ready.' };
    renderViews();
    setTimeout(() => DOM.mainWorkspace.scrollTop = 0, 50);
  }

  else if (action === 'set-lesson') {
    appState.activeLessonId = btn.dataset.id;
    appState.terminal = { status: 'idle', msg: 'Ready.' };

    const lesson = getActiveLessonObj();
    if (lesson && !appState.codeData[appState.activeLessonId]) {
      appState.codeData[appState.activeLessonId] = lesson.initialCode;
    }
    renderViews();
    setTimeout(() => DOM.mainWorkspace.scrollTop = 0, 50);
  }

  else if (action === 'run-code') {
    const lesson = getActiveLessonObj();
    if (!lesson) return;
    const userCode = appState.codeData[appState.activeLessonId] || '';

    if (lesson.validate(userCode)) {
      appState.terminal = { status: 'success', msg: lesson.successMsg };
      appState.completed[appState.activeLessonId] = true;
    } else {
      appState.terminal = { status: 'error', msg: lesson.errorMsg };
    }
    renderViews();
  }
});

// ==========================================
// 7. INITIALIZATION
// ==========================================
const initApp = () => {
  const initialLesson = getActiveLessonObj();
  if (initialLesson) {
    appState.codeData[appState.activeLessonId] = initialLesson.initialCode;
  }
  renderViews();
};

// Start App
initApp();
