function compileCustomGame(query) {
    const queryLower = query.toLowerCase();
    
    // 1. DETERMINE GENRE
    let genre = "snake";
    if (queryLower.includes("pong") || queryLower.includes("paddle") || queryLower.includes("hockey")) {
        genre = "pong";
    } else if (queryLower.includes("tic") || queryLower.includes("toe") || queryLower.includes("grid") || queryLower.includes("noughts")) {
        genre = "tictactoe";
    } else if (queryLower.includes("flap") || queryLower.includes("bird") || queryLower.includes("fly") || queryLower.includes("wing")) {
        genre = "flappy";
    } else if (queryLower.includes("brick") || queryLower.includes("break") || queryLower.includes("shatter") || queryLower.includes("ball") || queryLower.includes("breaker")) {
        genre = "snake";
    } else if (queryLower.includes("clicker") || queryLower.includes("cookie") || queryLower.includes("tap") || queryLower.includes("idle")) {
        genre = "snake";
    } else if (queryLower.includes("space") || queryLower.includes("shoot") || queryLower.includes("invader") || queryLower.includes("alien") || queryLower.includes("laser") || queryLower.includes("ship")) {
        genre = "snake";
    }

    // 2. DETERMINE THEME & PALETTE
    let theme = { name: "Classic Neon" };
    if (queryLower.includes("synthwave") || queryLower.includes("cyberpunk") || queryLower.includes("pink") || queryLower.includes("magenta") || queryLower.includes("neon")) {
        theme.name = "Neon Synthwave";
    } else if (queryLower.includes("matrix") || queryLower.includes("terminal") || queryLower.includes("hacker") || queryLower.includes("green")) {
        theme.name = "Hacker Matrix";
    } else if (queryLower.includes("ocean") || queryLower.includes("sea") || queryLower.includes("blue") || queryLower.includes("water") || queryLower.includes("underwater")) {
        theme.name = "Deep Ocean";
    } else if (queryLower.includes("sunset") || queryLower.includes("orange") || queryLower.includes("red") || queryLower.includes("fire") || queryLower.includes("volcano") || queryLower.includes("volcanos")) {
        theme.name = "Volcanic Sunset";
    } else if (queryLower.includes("forest") || queryLower.includes("garden") || queryLower.includes("wood") || queryLower.includes("emerald")) {
        theme.name = "Mystic Forest";
    }

    // 3. PARSE DIFFICULTY & SPEED
    let speedLabel = "Normal";
    if (queryLower.includes("fast") || queryLower.includes("speedy") || queryLower.includes("turbo") || queryLower.includes("rapid") || queryLower.includes("quick")) {
        speedLabel = "Turbo Speed";
    } else if (queryLower.includes("slow") || queryLower.includes("lazy") || queryLower.includes("chill") || queryLower.includes("relax")) {
        speedLabel = "Chill Speed";
    }

    const template = GAME_TEMPLATES[genre] || GAME_TEMPLATES.snake;
    return {
        title: "Custom " + theme.name + " " + genre.toUpperCase(),
        desc: `Custom compiled dynamic offline ${genre} template matching user criteria.`,
        code: template.code.replace(template.title || "", "Custom " + theme.name + " " + genre.toUpperCase()).replace("Normal", speedLabel)
    };
}
