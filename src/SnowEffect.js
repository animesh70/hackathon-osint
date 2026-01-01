import React, { useEffect, useRef } from 'react';

const SnowEffect = ({ intensity = 25, enabled = true }) => {
  const canvasRef = useRef(null);
  const snowflakes = useRef([]);
  const animationFrameId = useRef(null);

  useEffect(() => {
    if (!enabled) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Snowflake class
    class Snowflake {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height - canvas.height;
        this.radius = Math.random() * 1.5 + 1;
        this.speed = Math.random() * 0.5 + 0.3;
        this.wind = Math.random() * 0.3 - 0.15;
        this.opacity = Math.random() * 0.3 + 0.3;
        this.swing = Math.random() * 0.3;
        this.swingSpeed = Math.random() * 0.005 + 0.002;
        this.angle = 0;
      }

      update() {
        this.angle += this.swingSpeed;
        this.y += this.speed;
        this.x += Math.sin(this.angle) * this.swing + this.wind;

        // Reset if snowflake goes off screen
        if (this.y > canvas.height) {
          this.y = -10;
          this.x = Math.random() * canvas.width;
        }
        if (this.x > canvas.width + 10) {
          this.x = -10;
        } else if (this.x < -10) {
          this.x = canvas.width + 10;
        }
      }

      draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.font = `${this.radius * 4}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Add a subtle glow
        ctx.shadowBlur = 3;
        ctx.shadowColor = 'rgba(173, 216, 230, 0.3)';
        
        ctx.fillText('❄️', this.x, this.y);
        ctx.restore();
      }
    }

    // Initialize snowflakes
    snowflakes.current = [];
    for (let i = 0; i < intensity; i++) {
      snowflakes.current.push(new Snowflake());
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      snowflakes.current.forEach(snowflake => {
        snowflake.update();
        snowflake.draw();
      });

      animationFrameId.current = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [intensity, enabled]);

  if (!enabled) return null;

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-50"
      style={{ mixBlendMode: 'screen' }}
    />
  );
};

export default SnowEffect;