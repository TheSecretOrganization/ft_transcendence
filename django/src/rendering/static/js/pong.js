var Pong = (function () {
    const canvas = document.getElementById("gameCanvas");
    const context = canvas.getContext("2d");
    const paddleWidth = 10;
    const paddleHeight = 100;
    const paddleSpeed = 8;
    const ballRadius = 10;
    const ballBaseSpeed = 5;
    const colorFill = "white";
    const scoreFill = "white";
    const scoreFont = "20px Arial";
    const initLX = 0;
    const initRX = canvas.width - paddleWidth;
    const initY = canvas.height / 2 - paddleHeight / 2;
    const scoreToWin = 5;
    let lastPointWonByLeft = false;
    let animationFrameId;

    class Paddle {
        constructor(x, y, name) {
            this.x = x;
            this.y = y;
            this.move = 0;
            this.score = 0;
            this.name = name;
        }

        updatePosition() {
            this.y += this.move;
            this.y = Math.max(0, Math.min(this.y, canvas.height - paddleHeight));
        }

        draw() {
            context.fillStyle = colorFill;
            context.fillRect(this.x, this.y, paddleWidth, paddleHeight);
        }

        reset(x, y) {
            this.x = x;
            this.y = y;
            this.move = 0;
            this.score = 0;
        }
    }

    class Ball {
        constructor(x, y) {
            this.x = canvas.width / 2;
            this.y = canvas.height / 2;
            this.speed = {
                x: this.randomDirection(),
                y: this.randomDirection(),
            };
        }

        randomDirection() {
            return (Math.floor(Math.random() * 10) % 2) ? ballBaseSpeed : -ballBaseSpeed;
        }

        reset(fullReset = false) {
            this.x = canvas.width / 2;
            this.y = canvas.height / 2;
            if (fullReset) {
                this.speed.x = this.randomDirection();
            } else {
                this.speed.x = (lastPointWonByLeft) ? -ballBaseSpeed : ballBaseSpeed;
            }
            this.speed.y = this.randomDirection();
        }

        updatePosition() {
            this.x += this.speed.x;
            this.y += this.speed.y;
            this.checkWallCollision();
        }

        checkWallCollision() {
            if (this.y - ballRadius < 0 || this.y + ballRadius > canvas.height) {
                this.speed.y = -this.speed.y;
            }
        }

        checkLeftPaddleCollision(paddle) {
            if (this.x - ballRadius < paddle.x + paddleWidth &&
                this.y > paddle.y &&
                this.y < paddle.y + paddleHeight) {
                this.speed.x = -this.speed.x;
                this.speed.y += paddle.move * 0.5;
            }
        }

        checkRightPaddleCollision(paddle) {
            if (this.x + ballRadius > paddle.x &&
                this.y > paddle.y &&
                this.y < paddle.y + paddleHeight) {
                this.speed.x = -this.speed.x;
                this.speed.y += paddle.move * 0.5;
            }
        }

        checkOutOfBounds() {
            if (this.x - ballRadius < 0) {
                rightPaddle.score++;
                lastPointWonByLeft = false;
                this.reset();
            }
            else if (this.x + ballRadius > canvas.width) {
                leftPaddle.score++;
                lastPointWonByLeft = true;
                this.reset();
            }
        }

        draw() {
            context.beginPath();
            context.arc(this.x, this.y, ballRadius, 0, Math.PI * 2);
            context.fillStyle = colorFill;
            context.fill();
            context.closePath();
        }
    }

    const leftPaddle = new Paddle(initLX, initY, "Left");
    const rightPaddle = new Paddle(initRX, initY, "Right");
    const ball = new Ball();

    function handlePlayerInput(key, speed = 0) {
        switch (key) {
            case "w":
            case "W":
                leftPaddle.move = -speed;
                break;
            case "s":
            case "S":
                leftPaddle.move = speed;
                break;
            case "ArrowUp":
                rightPaddle.move = -speed;
                break;
            case "ArrowDown":
                rightPaddle.move = speed;
                break;
        };
    }

    function updateGame() {
        leftPaddle.updatePosition();
        rightPaddle.updatePosition();
        ball.updatePosition();
        ball.checkLeftPaddleCollision(leftPaddle);
        ball.checkRightPaddleCollision(rightPaddle);
        ball.checkOutOfBounds();
    }

    function drawText(text, x, y) {
        context.fillStyle = scoreFill;
        context.font = scoreFont;
        context.fillText(text, x, y);
    }

    function drawScore() {
        drawText(`${leftPaddle.name}: ${leftPaddle.score}`, 20, 20);
        drawText(`${rightPaddle.name}: ${rightPaddle.score}`, canvas.width - 80, 20);
    }

    function drawGame() {
        context.clearRect(0, 0, canvas.width, canvas.height);
        rightPaddle.draw();
        leftPaddle.draw();
        ball.draw();
        drawScore();
    }

    function drawWinner(winner) {
        context.clearRect(0, 0, canvas.width, canvas.height);
        const text = `Winner: ${winner}`;
        context.font = scoreFont;
        const textWidth = context.measureText(text).width;
        const x = (canvas.width - textWidth) / 2;
        const y = canvas.height / 2;
        drawText(text, x, y);
    }

    function checkScore() {
        if (leftPaddle.score >= scoreToWin || rightPaddle.score >= scoreToWin) {
            winner = leftPaddle.score >= scoreToWin ? leftPaddle.name : rightPaddle.name;
            drawWinner(winner);
            stop();
            document.getElementById("pongAgainBtn").style.display = "block";
            return true;
        }
        return false;
    }

    function gameLoop() {
        if (checkScore())
            return;
        updateGame();
        drawGame();
        animationFrameId = requestAnimationFrame(gameLoop);
    }

    function init() {
        document.addEventListener("keydown", function (e) { handlePlayerInput(e.key, paddleSpeed) });
        document.addEventListener("keyup", function (e) { handlePlayerInput(e.key, 0) });
        gameLoop();
    }

    function stop() {
        if (animationFrameId === undefined)
            return;
        cancelAnimationFrame(animationFrameId);
        animationFrameId = undefined;
        leftPaddle.reset(initLX, initY);
        rightPaddle.reset(initRX, initY);
        ball.reset(true);
        document.removeEventListener("keydown", handlePlayerInput);
        document.removeEventListener("keyup", handlePlayerInput);
    }

    return {
        start: function () {
            document.getElementById('gameSelection').style.display = 'none';
            document.getElementById('game').style.display = 'block';
            document.getElementById("pongAgainBtn").style.display = "none";
            init();
        },
        reset: function () {
            document.getElementById('gameSelection').style.display = 'block';
            document.getElementById('game').style.display = 'none';
            document.getElementById("pongAgainBtn").style.display = "none";
            stop();
        }
    };
})();

Array.from(document.getElementsByClassName('pongBtn')).forEach(function (button) {
    button.addEventListener('click', function () {
        Pong.start();
    });
});

document.getElementById('backBtn').addEventListener('click', function () {
    Pong.reset();
});
