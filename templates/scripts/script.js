const movableDot=document.getElementById('movable-dot');

let isDragging=false;

// change mouse cursor style when "grabbing" the dot
movableDot.addEventListener("mousedown",(e)=>{
    isDragging=true;
    movableDot.style.cursor="grabbing";
})

document.addEventListener("mousemove",(e)=>{
    if(!isDragging) return;

    const x=e.clientX;// get mouse x position
    const y=e.clientY;// get mouse y position

    movableDot.style.left=x-movableDot.offsetWidth/2+"px";// set dot x position
    movableDot.style.top=y-movableDot.offsetHeight/2+"px";// set dot y position
})

document.addEventListener("mouseup",()=>{
    isDragging=false;
    movableDot.style.cursor="grab";
})