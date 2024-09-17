const data = document.currentScript.dataset
const stat = data.status
const id = data.id
const status_elem = document.querySelector('#status')
const btn = document.querySelector('#btn')
status_elem.textContent = stat
switch(Number(id)){
    case(1):
    status_elem.classList.add('bg-secondary');
    btn.style.display('hidden')
    break;
    case(2):
    btn.style.display('hidden')
    status_elem.classList.add('bg-info');
    break;
    case(3):
    status_elem.classList.add('bg-primary');
    btn.style.display('block')
    break;
    case(4):
    status_elem.classList.add('bg-success');
    break;
    case(5):
    status_elem.classList.add('bg-danger');
    break;
    default:
        status_elem.classList.add('bg-primary')
}

