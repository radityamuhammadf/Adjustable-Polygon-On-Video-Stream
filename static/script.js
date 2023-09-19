const rectangle = document.getElementById('rectangle');
const dots = document.querySelectorAll('.dot');

let isDragging = false;
let currentDot = null;
let startX, startY, startWidth, startHeight;

dots.forEach(dot => {
   dot.addEventListener('mousedown', (e) => {
       isDragging = true;
       currentDot = dot;
       startX = e.clientX;
       startY = e.clientY;
       startWidth = parseFloat(getComputedStyle(rectangle).width);
       startHeight = parseFloat(getComputedStyle(rectangle).height);
       e.preventDefault();
   });
});

document.addEventListener('mousemove', (e) => {
   if (!isDragging) return;

   const offsetX = e.clientX - startX;
   const offsetY = e.clientY - startY;

   switch (currentDot.id) {
       case 'top-left':
           rectangle.style.width = startWidth - offsetX + 'px';
           rectangle.style.height = startHeight - offsetY + 'px';
           rectangle.style.left = startX + offsetX + 'px';
           rectangle.style.top = startY + offsetY + 'px';
           break;
       case 'top-right':
           rectangle.style.width = startWidth + offsetX + 'px';
           rectangle.style.height = startHeight - offsetY + 'px';
           rectangle.style.top = startY + offsetY + 'px';
           break;
       case 'bottom-left':
           rectangle.style.width = startWidth - offsetX + 'px';
           rectangle.style.height = startHeight + offsetY + 'px';
           rectangle.style.left = startX + offsetX + 'px';
           break;
       case 'bottom-right':
           rectangle.style.width = startWidth + offsetX + 'px';
           rectangle.style.height = startHeight + offsetY + 'px';
           break;
   }
});

document.addEventListener('mouseup', () => {
   isDragging = false;
   currentDot = null;
});
