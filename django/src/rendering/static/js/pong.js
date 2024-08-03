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
    const initRX = 0;
    const initLX = canvas.width - paddleWidth;
    const initY = canvas.height / 2 - paddleHeight / 2;
    let lastPointWonByLeft = false;
    let animationFrameId;

    class Paddle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.move = 0;
            this.score = 0;
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

    const rightPaddle = new Paddle(initRX, initY);
    const leftPaddle = new Paddle(initLX, initY);
    const ball = new Ball();

    function listenPlayerInput(input, speed = 0) {
        document.addEventListener(input, function (e) {
            switch (e.key) {
                case "w":
                case "W":
                case "ArrowUp":
                    rightPaddle.move = -speed;
                    break;
                case "s":
                case "S":
                case "ArrowDown":
                    rightPaddle.move = speed;
                    break;
            }
        });
    }

    function handleAi() {
        if (ball.y < leftPaddle.y + paddleHeight / 2) {
            leftPaddle.y -= paddleSpeed;
        } else {
            leftPaddle.y += paddleSpeed;
        }

        leftPaddle.y = Math.max(0, Math.min(leftPaddle.y, canvas.height - paddleHeight));
    }

    function updateGame() {
        rightPaddle.updatePosition();
        ball.updatePosition();
        ball.checkLeftPaddleCollision(rightPaddle);
        ball.checkRightPaddleCollision(leftPaddle);
        ball.checkOutOfBounds();
        handleAi();
    }

    function drawPoints() {
        context.fillStyle = scoreFill;
        context.font = scoreFont;
        context.fillText(`Player: ${leftPaddle.score}`, 20, 20);
        context.fillText(`AI: ${rightPaddle.score}`, canvas.width - 80, 20);
    }

    function drawGame() {
        context.clearRect(0, 0, canvas.width, canvas.height);
        rightPaddle.draw();
        leftPaddle.draw();
        ball.draw();
        drawPoints();
    }

    function gameLoop() {
        updateGame();
        drawGame();
        animationFrameId = requestAnimationFrame(gameLoop);
    }

    function init() {
        listenPlayerInput("keydown", paddleSpeed);
        listenPlayerInput("keyup");
        gameLoop();
    }

    function stop() {
        cancelAnimationFrame(animationFrameId);
        leftPaddle.reset(initLX, initY);
        rightPaddle.reset(initRX, initY);
        ball.reset(true);
        document.removeEventListener("keydown");
        document.removeEventListener("keyup");
    }

    return {
        start: function() {
            document.querySelectorAll('.startBtn').forEach(btn => btn.style.display = 'none');
            document.getElementById('backBtn').style.display = 'block';
            canvas.style.display = 'block';
            init();
        },
        reset: function() {
            document.querySelectorAll('.startBtn').forEach(btn => btn.style.display = 'block');
            document.getElementById('backBtn').style.display = 'none';
            canvas.style.display = 'none';
            stop();
        }
    };
})();

document.getElementById('pongBtn').addEventListener('click', function() {
    Pong.start();
});

document.getElementById('backBtn').addEventListener('click', function() {
    Pong.reset();
});
