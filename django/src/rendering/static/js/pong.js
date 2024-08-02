const canvas = document.getElementById("pongCanvas");
const context = canvas.getContext("2d");
const paddleWidth = 10;
const paddleHeight = 100;
const paddleSpeed = 8;
const ballRadius = 10;
const ballBaseSpeed = 5;

class Paddle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.move = 0;
    }
}

const playerPaddle = new Paddle(0, canvas.height / 2 - paddleHeight / 2);
const aiPaddle = new Paddle(canvas.width - paddleWidth, canvas.height / 2 - paddleHeight / 2);
let ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    speed: {
        x: ballBaseSpeed,
        y: ballBaseSpeed,
    }
};

function listenPlayerInput(input, speed = 0) {
    document.addEventListener(input, function(e) {
        switch(e.key) {
            case "w":
            case "W":
                console.log("test");
                playerPaddle.move = -speed;
                break;
            case "s":
            case "S":
                console.log("test2");
                playerPaddle.move = speed;
                break;
        }
    });
}

function checkWallColision() {
    if (ball.y - ballRadius < 0 || ball.y + ballRadius > canvas.height) {
        ball.speed.y = -ball.speed.y;
    }
}

function checkPaddleCollision() {
    if (ball.x - ballRadius < playerPaddle.x + paddleWidth &&
        ball.y > playerPaddle.y &&
        ball.y < playerPaddle.y + paddleHeight) {
        ball.speed.x = -ball.speed.x;
    }

    if (ball.x + ballRadius > aiPaddle.x &&
        ball.y > aiPaddle.y &&
        ball.y < aiPaddle.y + paddleHeight) {
        ball.speed.x = -ball.speed.x;
    }
}

function checkBallOutOfBounds() {
    if (ball.x - ballRadius < 0 || ball.x + ballRadius > canvas.width) {
        ball.x = canvas.width / 2;
        ball.y = canvas.height / 2;
        ball.speed.x = ballBaseSpeed;
        ball.speed.y = ballBaseSpeed;
    }
}

function handleAi() {
    if (ball.y < aiPaddle.y + paddleHeight / 2) {
        aiPaddle.y -= paddleSpeed;
    } else {
        aiPaddle.y += paddleSpeed;
    }

    if (aiPaddle.y < 0) {
        aiPaddle.y = 0;
    } else if (aiPaddle.y + paddleHeight > canvas.height) {
        aiPaddle.y = canvas.height - paddleHeight;
    }
}

function update() {
    playerPaddle.y += playerPaddle.move;
    if (playerPaddle.y < 0) {
        playerPaddle.y = 0;
    } else if (playerPaddle.y + paddleHeight > canvas.height) {
        playerPaddle.y = canvas.height - paddleHeight;
    }

    ball.x += ball.speed.x;
    ball.y += ball.speed.y;

    checkWallColision();
    checkPaddleCollision();
    checkBallOutOfBounds();

    handleAi();
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    context.fillStyle = "black";
    context.fillRect(playerPaddle.x, playerPaddle.y, paddleWidth, paddleHeight);

    context.fillStyle = "black";
    context.fillRect(aiPaddle.x, aiPaddle.y, paddleWidth, paddleHeight);

    context.beginPath();
    context.arc(ball.x, ball.y, ballRadius, 0, Math.PI * 2);
    context.fillStyle = "black";
    context.fill();
    context.closePath();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function initGame() {
    listenPlayerInput("keydown", paddleSpeed);
    listenPlayerInput("keyup");
    gameLoop();
}

initGame();
