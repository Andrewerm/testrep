window.addEventListener('load',()=> {
    id_selectShippingFrom.addEventListener('change', function () {
        id_selectShippingFrom.querySelectorAll('li').forEach(item => {
            const elem = item.querySelector('label input');
            document.getElementById(`id_${elem.value}`).hidden = !elem.checked
        })
    })
    id_fromChelny.hidden = 'hidden'
})
