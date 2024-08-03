var Pong = (function() {
    const canvas = document.getElementById("pongCanvas");
    const context = canvas.getContext("2d");
    const paddleWidth = 10;
    const paddleHeight = 100;
    const paddleSpeed = 8;
    const ballRadius = 10;
    const ballBaseSpeed = 5;
    const colorFill = "white";

    class Paddle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.move = 0;
        }

        updatePosition() {
            this.y += this.move;
            this.y = Math.max(0, Math.min(this.y, canvas.height - paddleHeight));
        }

        draw() {
            context.fillStyle = colorFill;
            context.fillRect(this.x, this.y, paddleWidth, paddleHeight);
        }
    }

    class Ball {
        constructor(x, y, speedX, speedY) {
            this.x = x;
            this.y = y;
            this.speed = {
                x: speedX,
                y: speedY,
            };
        }

        reset() {
            this.x = canvas.width / 2;
            this.y = canvas.height / 2;
            this.speed.x = ballBaseSpeed;
            this.speed.y = ballBaseSpeed;
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
            }
        }

        checkRightPaddleCollision(paddle) {
            if (this.x + ballRadius > paddle.x &&
                this.y > paddle.y &&
                this.y < paddle.y + paddleHeight) {
                this.speed.x = -this.speed.x;
            }
        }

        checkOutOfBounds() {
            if (this.x - ballRadius < 0 || this.x + ballRadius > canvas.width) {
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

    const playerPaddle = new Paddle(0, canvas.height / 2 - paddleHeight / 2);
    const aiPaddle = new Paddle(canvas.width - paddleWidth, canvas.height / 2 - paddleHeight / 2);
    const ball = new Ball(canvas.width / 2, canvas.height / 2, ballBaseSpeed, ballBaseSpeed);

    function listenPlayerInput(input, speed = 0) {
        document.addEventListener(input, function (e) {
            switch (e.key) {
                case "w":
                case "W":
                case "ArrowUp":
                    playerPaddle.move = -speed;
                    break;
                case "s":
                case "S":
                case "ArrowDown":
                    playerPaddle.move = speed;
                    break;
            }
        });
    }

    function handleAi() {
        if (ball.y < aiPaddle.y + paddleHeight / 2) {
            aiPaddle.y -= paddleSpeed;
        } else {
            aiPaddle.y += paddleSpeed;
        }

        aiPaddle.y = Math.max(0, Math.min(aiPaddle.y, canvas.height - paddleHeight));
    }

    function updateGame() {
        playerPaddle.updatePosition();
        ball.updatePosition();
        ball.checkLeftPaddleCollision(playerPaddle);
        ball.checkRightPaddleCollision(aiPaddle);
        ball.checkOutOfBounds();
        handleAi();
    }

    function drawGame() {
        context.clearRect(0, 0, canvas.width, canvas.height);
        playerPaddle.draw();
        aiPaddle.draw();
        ball.draw();
    }

    function gameLoop() {
        updateGame();
        drawGame();
        requestAnimationFrame(gameLoop);
    }

    return {
        init: function() {
            listenPlayerInput("keydown", paddleSpeed);
            listenPlayerInput("keyup");
            gameLoop();
        }
    };
})();

Pong.init();
