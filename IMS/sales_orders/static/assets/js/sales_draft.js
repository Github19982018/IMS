form = document.querySelector('#sales_draft') 
document.querySelector('#datein').value = new Date().toLocaleString()
document.querySelector('#total').textContent = Number(document.querySelector('#sub').textContent) + Number(document.querySelector('#discount').val);
// form.addEventListener('submit',(e) => {
// e.preventDefault()
// fetch(location.host+'/ims/v1/sales/save',{
//     method:'post',
//     body :{
//         'total_price':document.querySelector('#total'),
//         'offer':document.querySelector('#discount')
//     }
// })
// form.submit()
// })

