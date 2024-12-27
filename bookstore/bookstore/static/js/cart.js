function addToCart(ma_sach, ten_sach, gia) {
    event.preventDefault() // Ngăn hành động mặc định của nút
    //promise

    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({
            'ma_sach': ma_sach,
            'ten_sach': ten_sach,
            'gia': gia
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementById('cartCounter')
        counter.innerText = data.total_quantity
    }).catch(function(err) {
        console.error(err)
    })
}

function pay() {
    if (confirm('Bạn chắc chắn muốn thanh toán không?')) {
        fetch('/api/pay', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json())
          .then(data => {
              console.log('Dữ liệu trả về từ server:', data);  // In kết quả trả về từ API
              if (data.code == 200) {
                  location.reload();  // Reload trang sau khi thanh toán thành công
              } else {
                  console.log(`Lỗi thanh toán: ${data.message || 'Không xác định'}`);
                  alert(`Lỗi thanh toán: ${data.message || 'Không xác định'}`);
              }
          })
          .catch(err => {
              console.error('Lỗi khi gọi API:', err);  // In lỗi nếu gặp sự cố khi gọi API
              alert('Có lỗi xảy ra khi thanh toán. Vui lòng thử lại!');
          });
    }
}

function order() {
    if (confirm('Bạn chắc chắn muốn đặt hàng không?')) {
        fetch('/api/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json())
          .then(data => {
              console.log('Dữ liệu trả về từ server:', data);  // In kết quả trả về từ API
              if (data.code == 200) {
                  location.reload();  // Reload trang sau khi thanh toán thành công
              } else {
                  console.log(`Lỗi đặt hàng: ${data.message || 'Không xác định'}`);
                  alert(`Lỗi đặt hàng: ${data.message || 'Không xác định'}`);
              }
          })
          .catch(err => {
              console.error('Lỗi khi gọi API:', err);  // In lỗi nếu gặp sự cố khi gọi API
              alert('Có lỗi xảy ra khi đặt hàng. Vui lòng thử lại!');
          });
    }
}

function updateQuantity(productId, quantity) {
    fetch('/update-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: productId,
            quantity: quantity
            })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {

            location.reload(); // Tải lại trang để cập nhật giao diện
        } else {
            alert('Có lỗi xảy ra khi cập nhật số lượng.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Không thể cập nhật số lượng.');
    });
}

function deleteCart(productId) {
    fetch(`/api/delete-cart/${productId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.code === 200) {
            // Cập nhật lại giỏ hàng trên giao diện nếu cần
            location.reload();  // Reload trang hoặc cập nhật giỏ hàng
        } else {
            alert(data.message);  // Hiển thị thông báo lỗi
        }
    })
    .catch(err => {
        console.error('Lỗi khi xóa sản phẩm:', err);
        alert('Có lỗi xảy ra khi xóa sản phẩm. Vui lòng thử lại!');
    });
}


function addComment(maSach) {
    let content = document.getElementById('commentId');
    if (content !== null) {
        fetch('/api/comments', {
            method: 'POST',
            body: JSON.stringify({
                'ma_sach': maSach,
                'content': content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) { // Changed from 201 to 200 to match your backend
                let comment = data.comment;
                let area = document.getElementById('commentArea');
                area.innerHTML = `
                    <div class="row">
                        <div class="col-md-1">
                            <img src="${comment.user.avatar}" class="img-fluid rounded-circle" alt="demo" />
                        </div>
                        <div class="col-md-10">
                            <p>${comment.content}</p>
                            <p>${comment.created_date}</p>
                        </div>
                    </div>
                ` + area.innerHTML;

                // Clear the comment input after successful submission
                content.value = '';
            } else {
                alert('Error posting comment');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error posting comment');
        });
    }
}