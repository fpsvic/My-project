const OFFLINE_KNOWLEDGE_BASE = {
    javascript: {
        concurrency: {
            title: "Asynchronous Concurrency Queue",
            desc: "JavaScript coordinates highly concurrent micro-processes natively using a single-threaded **Event Loop** protocol.",
            code: `class MicroTaskScheduler {\n    constructor(limit = 3) {\n        this.limit = limit; this.running = 0; this.queue = [];\n    }\n    async add(task) {\n        return new Promise((resolve, reject) => {\n            this.queue.push({ task, resolve, reject }); this.process();\n        });\n    }\n    process() {\n        if (this.running >= this.limit || !this.queue.length) return;\n        this.running++; const { task, resolve, reject } = this.queue.shift();\n        queueMicrotask(async () => {\n            try { resolve(await task()); } catch (err) { reject(err); } finally { this.running--; this.process(); }\n        });\n    }\n}`
        },
        datastructure: {
            title: "O(1) Least-Recently-Used (LRU) Cache",
            desc: "An LRU Cache requires $O(1)$ lookup, insertion, and eviction bounds dynamically.",
            code: `class LRUNode {\n    constructor(key, value) {\n        this.key = key; this.value = value; this.prev = null; this.next = null;\n    }\n}\nclass LRUCache {\n    constructor(capacity) {\n        this.capacity = capacity; this.map = new Map();\n        this.head = new LRUNode(0, 0); this.tail = new LRUNode(0, 0);\n        this.head.next = this.tail; this.tail.prev = this.head;\n    }\n    _remove(node) {\n        node.prev.next = node.next; node.next.prev = node.prev;\n    }\n    _insertAtHead(node) {\n        node.next = this.head.next; node.next.prev = node; this.head.next = node; node.prev = this.head;\n    }\n    get(key) {\n        if (!this.map.has(key)) return -1;\n        const node = this.map.get(key); this._remove(node); this._insertAtHead(node);\n        return node.value;\n    }\n}`
        },
        default: {
            title: "Prototype & Functional Composition Primitives",
            desc: "JavaScript leverages closures, prototypal hierarchies, and higher-order composition loops.",
            code: `const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);\nconst curry = (fn) => {\n    return function curried(...args) {\n        if (args.length >= fn.length) return fn.apply(this, args);\n        return (...args2) => curried.apply(this, args.concat(args2));\n    };\n};`
        }
    }
};
OFFLINE_KNOWLEDGE_BASE.typescript = OFFLINE_KNOWLEDGE_BASE.javascript;
OFFLINE_KNOWLEDGE_BASE.luascript = OFFLINE_KNOWLEDGE_BASE.javascript;
OFFLINE_KNOWLEDGE_BASE.csharp = OFFLINE_KNOWLEDGE_BASE.javascript;
