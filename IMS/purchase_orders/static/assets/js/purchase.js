const data = document.currentScript.dataset
const stat = data.status
const id = data.id
const cancel = data.cancel
const status_elem = document.querySelector('#status')
const btn = document.querySelector('#btn')
status_elem.textContent = data.cancel? 'cancelled': stat;
if(cancel){
    status_elem.classList.add('bg-dark');
    document.querySelector(':root').style.setProperty('--progress-bg','rgb(0,0,0)');
}
else{
    switch(Number(id)){
        case(1):
        status_elem.classList.add('bg-secondary');
        break;
        case(2):
        status_elem.classList.add('bg-info');
        break;
        case(3):
        status_elem.classList.add('bg-primary');
        break;
        case(4):
        status_elem.classList.add('bg-success');
        break;
        case(5):
        status_elem.classList.add('bg-info');
        break;
        case(7):
        status_elem.classList.add('bg-dark');
        document.querySelector(':root').style.setProperty('--progress-bg','rgb(0,0,0)');
        break;
        default:
            status_elem.classList.add('bg-primary')
    }
}