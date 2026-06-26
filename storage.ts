interface Project {
    id: string;
    name: string;
    files: Record<string, string>;
    currentFile: string;
    lang: string;
}

type FileMap = Record<string, string>;

class JungleStorage {
    static getProjects(): Project[] {
        const data = localStorage.getItem('jungle_sandbox_projects');
        if (data) {
            try { return this.normalizeProjects(JSON.parse(data)); } catch(e) { return this.getDefaultProjects(); }
        }
        return this.getDefaultProjects();
    }
    static saveProjects(list: Project[]): void { localStorage.setItem('jungle_sandbox_projects', JSON.stringify(list)); }
    static getDefaultProjects(): Project[] { return []; }
    static normalizeProjects(list: unknown[]): Project[] {
        if (!Array.isArray(list)) return [];
        return list.map((project: any, index: number): Project => {
            const files: FileMap = project && project.files && typeof project.files === 'object' ? project.files : { 'index.html': '' };
            if (Object.keys(files).length === 0) files['index.html'] = '';
            const fileNames = Object.keys(files);
            const currentFile: string = project && files[project.currentFile] !== undefined ? project.currentFile : fileNames[0];
            const lang: string = (project && project.lang) || JungleIntelligence.languageFromFilename(currentFile, 'HTML');
            return {
                id: (project && project.id) || `proj_${Date.now()}_${index}`,
                name: (project && project.name) || `Project ${index + 1}`,
                files,
                currentFile,
                lang
            };
        });
    }
}
class JungleIntelligence {
    static readonly languageExtensions: Record<string, string> = {
        'HTML': '.html',
        'Javascript': '.js',
        'TypeScript': '.ts',
        'Python': '.py',
        'C++': '.cpp',
        'C': '.c',
        'Java': '.java',
        'C#': '.cs',
        'Ruby': '.rb',
        'Go': '.go',
        'Rust': '.rs',
        'PHP': '.php',
        'Swift': '.swift',
        'Kotlin': '.kt',
        'Scala': '.scala',
        'R': '.r',
        'Perl': '.pl',
        'Haskell': '.hs',
        'Julia': '.jl',
        'Lua': '.lua',
        'Clojure': '.clj',
        'Elixir': '.ex',
        'Erlang': '.erl',
        'OCaml': '.ml',
        'F#': '.fs',
        'Dart': '.dart',
        'Bash': '.sh',
        'Fortran': '.f90',
        'COBOL': '.cob',
        'D': '.d',
        'Zig': '.zig',
        'Nim': '.nim',
        'Assembly': '.asm',
        'Lisp': '.lisp',
        'Prolog': '.pl',
        'Pascal': '.pas'
    };
    static readonly extensionLanguages: Record<string, string> = {
        '.html': 'HTML',
        '.htm': 'HTML',
        '.js': 'Javascript',
        '.mjs': 'Javascript',
        '.cjs': 'Javascript',
        '.ts': 'TypeScript',
        '.py': 'Python',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.c': 'C',
        '.java': 'Java',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.pl': 'Perl',
        '.hs': 'Haskell',
        '.jl': 'Julia',
        '.lua': 'Lua',
        '.clj': 'Clojure',
        '.ex': 'Elixir',
        '.erl': 'Erlang',
        '.ml': 'OCaml',
        '.fs': 'F#',
        '.dart': 'Dart',
        '.sh': 'Bash',
        '.bash': 'Bash',
        '.f90': 'Fortran',
        '.cob': 'COBOL',
        '.d': 'D',
        '.zig': 'Zig',
        '.nim': 'Nim',
        '.asm': 'Assembly',
        '.s': 'Assembly',
        '.lisp': 'Lisp',
        '.pas': 'Pascal'
    };
    static getExtension(name: string): string {
        const match = String(name || '').toLowerCase().match(/(\.[a-z0-9+#]+)$/);
        return match ? match[1] : "";
    }
    static getDefaultExtension(lang: string): string {
        return this.languageExtensions[lang] || '.txt';
    }
    static languageFromFilename(filename: string, fallback: string = 'Javascript'): string {
        return this.extensionLanguages[this.getExtension(filename)] || fallback;
    }
    static sanitizeFileName(input: string, lang: string = 'Javascript', existingFiles: FileMap = {}): string {
        let name = String(input || '').trim().replace(/[\\/:*?"<>|]+/g, '-').replace(/\s+/g, '-');
        name = name.replace(/^-+|-+$/g, '');
        if (!name) name = 'main';
        if (!this.getExtension(name)) name += this.getDefaultExtension(lang);
        const base = name.replace(/(\.[^.]+)$/, '');
        const ext = this.getExtension(name);
        let candidate = name;
        let counter = 2;
        while (Object.prototype.hasOwnProperty.call(existingFiles, candidate)) {
            candidate = `${base}-${counter}${ext}`;
            counter++;
        }
        return candidate;
    }
    static guessProjectLanguage(name: string): string {
        const text = String(name || '').toLowerCase();
        if (/python|py|data|math|ai|ml/.test(text)) return 'Python';
        if (/type|ts|typescript/.test(text)) return 'TypeScript';
        if (/html|web|site|page|frontend|browser/.test(text)) return 'HTML';
        if (/java\b|android/.test(text)) return 'Java';
        if (/c\+\+|cpp|game|engine/.test(text)) return 'C++';
        if (/\bc\b|clang/.test(text)) return 'C';
        if (/go|golang/.test(text)) return 'Go';
        if (/rust|rs/.test(text)) return 'Rust';
        return 'HTML';
    }
    static createStarterProject(id: string, name: string): Project {
        const lang = this.guessProjectLanguage(name);
        const defaultFile = JungleIntelligence.getDefaultExtension(lang)
            ? `main${JungleIntelligence.getDefaultExtension(lang)}`
            : (lang === 'HTML' ? 'index.html' : 'main.txt');
        return { id, name, files: { [defaultFile]: '' }, currentFile: defaultFile, lang };
    }
    static renameFileForLanguage(filename: string, lang: string, files: FileMap): string {
        const desiredExt = this.getDefaultExtension(lang);
        if (!desiredExt || filename.toLowerCase().endsWith(desiredExt)) return filename;
        const next = filename.replace(/(\.[^.]+)?$/, desiredExt);
        if (!Object.prototype.hasOwnProperty.call(files, next)) return next;
        return filename;
    }
    static injectProjectAssetsIntoHtml(html: string, files: FileMap): string {
        let output = html;
        Object.keys(files).forEach(filename => {
            const lower = filename.toLowerCase();
            if (lower.endsWith('.css')) {
                const linkPattern = new RegExp(`<link[^>]+href=["']${this.escapeRegExp(filename)}["'][^>]*>`, 'i');
                output = output.replace(linkPattern, `<style data-jungle-file="${filename}">\n${files[filename]}\n</style>`);
            } else if (lower.endsWith('.js')) {
                const scriptPattern = new RegExp(`<script[^>]+src=["']${this.escapeRegExp(filename)}["'][^>]*>\\s*<\\/script>`, 'i');
                output = output.replace(scriptPattern, `<script data-jungle-file="${filename}">\n${files[filename]}\n<\\/script>`);
            }
        });
        return output;
    }
    static findMissingHtmlAssets(html: string, files: FileMap): Array<{ file: string; line: number }> {
        const missing: Array<{ file: string; line: number }> = [];
        const assetRegex = /<(script|link)[^>]+(?:src|href)=["']([^"']+)["'][^>]*>/gi;
        let match: RegExpExecArray | null;
        while ((match = assetRegex.exec(html)) !== null) {
            const assetPath = match[2];
            if (/^(https?:)?\/\//i.test(assetPath) || assetPath.startsWith('data:') || assetPath.startsWith('#')) continue;
            const cleanPath = assetPath.replace(/^\.\//, '').split(/[?#]/)[0];
            if (!Object.prototype.hasOwnProperty.call(files, cleanPath)) {
                const line = html.slice(0, match.index).split('\n').length;
                missing.push({ file: cleanPath, line });
            }
        }
        return missing;
    }
    static escapeRegExp(value: string): string {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}
