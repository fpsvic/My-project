const LANG_HISTORY = {
    python: "Python was conceived in the late 1980s by Guido van Rossum in the Netherlands as an ABC successor. Officially released in 1991, it was named after Monty Python's Flying Circus. It emphasizes code readability ('Zen of Python') and dominates data science and ML.",
    java: "Java was developed by James Gosling and team at Sun Microsystems in 1995. Originally called Oak, it was retargeted for the Web under the slogan 'Write Once, Run Anywhere' (WORA) using JVM bytecode execution. It dominates enterprise systems.",
    javascript: "JavaScript was designed in 1995 by Brendan Eich at Netscape in just 10 days under the codename Mocha. Rebranded to piggyback on Java's popularity, it was standardized under ECMAScript and became the ubiquitous engine of the modern web.",
    typescript: "TypeScript was designed by Anders Hejlsberg at Microsoft in 2012 to solve JavaScript scalability challenges. It is a typed superset compiling directly to JS, adding static typings without any runtime overhead.",
    golang: "Go (Golang) was designed at Google in 2007 by Robert Griesemer, Rob Pike, and Ken Thompson. Released in 2009, it addresses slow compilations and systems complexity with goroutines, channels, and zero-overhead binary builds.",
    cpp: "C++ was created by Bjarne Stroustrup in 1979 at Bell Laboratories. Originally 'C with Classes', it added Simula's abstractions to C's bare-metal speed. Standardized in 1983, it runs low-latency systems and game engines.",
    c: "C was designed by Dennis Ritchie at Bell Labs between 1969 and 1973 to rewrite Unix. It provided structured paradigms with a direct mapping to assembly, making it the most influential foundation for OS kernels and firmware.",
    csharp: "C# was designed by Anders Hejlsberg at Microsoft in 2000 as part of .NET. Designed as a modern object-oriented competitor to Java, it runs enterprise backends, desktop apps, and Unity games today.",
    rust: "Rust began as a personal research project by Graydon Hoare in 2006, sponsored by Mozilla in 2009 to replace C++ browser engines. Officially released in 2015, it guarantees memory and thread safety at compile-time without a GC.",
    swift: "Swift was developed at Apple by Chris Lattner beginning in 2010. Released in 2014 as a modern successor to Objective-C, it delivers compiled systems-level speed with a clean script-like syntax.",
    kotlin: "Kotlin was designed by JetBrains in 2010 and named after Kotlin Island. Built to solve Java pain points while remaining 100% interoperable, it became Google's preferred language for Android in 2017.",
    lua: "Lua was created in 1993 by Roberto Ierusalimschy and team in Brazil. Designed as a lightweight, embeddable C-compatible scripting language, its tiny memory footprint made it an industry standard for games and IoT.",
    luau: "Luau is Roblox's statically typed derivative of Lua 5.1. It adds a robust type system, aggressive compiler optimizations, and specialized vector instructions to safely run millions of concurrent game scripts.",
    matlab: "MATLAB was designed by Cleve Moler in the late 1970s to give students easy, interactive access to LINPACK/EISPACK. Commercialized by MathWorks in 1984, it is the global standard for matrix computation and scientific analysis.",
    r: "R was created by Ross Ihaka and Robert Gentleman in 1993 in New Zealand. As an open-source dialect of S, it is specifically engineered for statistical computing, data analysis, and advanced graphics.",
    ruby: "Ruby was designed by Yukihiro Matsumoto in 1995. Focused on developer happiness and human readability, it gained global adoption in the mid-2000s through the Ruby on Rails web framework."
};

const LANG_HELLO_WORLD = {
    javascript: 'console.log("Hello, World!");',
    typescript: 'const greeting: string = "Hello, World!";\nconsole.log(greeting);',
    java: 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
    golang: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
    cpp: '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
    c: '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
    csharp: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}',
    kotlin: 'fun main() {\n    println("Hello, World!")\n}',
    lua: 'print("Hello, World!")',
    luau: 'print("Hello, World!")',
    matlab: "disp('Hello, World!');",
    python: 'print("Hello, World!")',
    r: 'print("Hello, World!")',
    ruby: 'puts "Hello, World!"',
    rust: 'fn main() {\n    println!("Hello, World!");\n}',
    swift: 'print("Hello, World!")'
};

const spaceKeywords = ["sun", "earth", "moon", "mars", "space", "astronom", "galaxy", "universe", "distance", "miles", "gravity", "orbit", "planet", "speed of light", "cosmic", "sol", "luna", "star", "solar"];
const earthKeywords = ["rock", "mineral", "stone", "geolog", "petrolog", "basalt", "granite", "sediment", "metamorph", "igneous", "volcano", "lava", "magma", "magmatic", "caldera", "tectonic", "plate", "ring of fire", "subduction", "trench", "mariana", "ocean", "underwater", "hydrothermal", "vent", "black smoker", "seafloor", "crust", "mantle", "mohs"];
const advancedScienceKeywords = ["quantum", "physics", "planck", "boltzmann", "chemistry", "element", "carbon", "noble", "electroneg", "dna", "gene", "cell", "transcription", "biology", "golden ratio", "phi", "euler", "irrational"];
const politicalKeywords = ["washington", "president", "lincoln", "fdr", "new deal", "civil war", "party", "whig", "federalist", "constitution", "politic", "align"];
