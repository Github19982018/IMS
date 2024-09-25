// form = document.querySelector('#sales_draft') 
// document.querySelector('#datein').value = new Date().toLocaleString()
// document.querySelector('#total').textContent = Number(document.querySelector('#sub').textContent) + Number(document.querySelector('#discount').val);
// form.addEventListener('submit',(e) => {


// window.addEventListener('beforeunload', function(e) {
//     this.alert("Are you sure to leave? All changes will be lost.")
//     e.preventDefault()
//     return ("Are you sure to leave? All changes will be lost.")
// })


const data = document.currentScript.dataset
const stat = data.status
const id = data.id
const status_elem = document.querySelector('#status')
const btn = document.querySelector('#btn')
status_elem.textContent = stat
switch(Number(id)){
    case(1):
    status_elem.classList.add('bg-secondary');
    btn.classList.add('d-block');
    break;
    case(2):
    btn.classList.add('d-block');
    status_elem.classList.add('bg-info');
    break;
    case(3):
    status_elem.classList.add('bg-primary');
    btn.classList.add('d-none');
    break;
    case(4):
    status_elem.classList.add('bg-success');
    btn.classList.add('d-none');
    break;
    case(5):
    status_elem.classList.add('bg-danger');
    btn.classList.remove('d-block');
    break;
    default:
        status_elem.classList.add('bg-primary')
}

