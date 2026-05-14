/* ========================================
   TOKYOROLL - Admin Panel JavaScript
   ======================================== */

// Документ загружен
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin panel loaded');
    
    // Инициализация всех компонентов
    initSidebar();
    initStatusButtons();
    initDeleteConfirmations();
    initImagePreview();
    initFormValidation();
    initAutoSlug();
    initDatePickers();
    initCharts();
    initNotifications();
});

// ----- 1. Sidebar Toggle (для мобильных устройств) -----
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarCollapse');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('content').classList.toggle('active');
        });
    }
}

// ----- 2. Быстрое изменение статуса заказа (AJAX) -----
function initStatusButtons() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const orderId = this.getAttribute('data-order-id');
            const newStatus = this.value;
            
            updateOrderStatus(orderId, newStatus);
        });
    });
}

function updateOrderStatus(orderId, status) {
    fetch(`/admin_panel/orders/${orderId}/status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Статус заказа обновлен!', 'success');
        } else {
            showNotification('Ошибка при обновлении', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка сервера', 'error');
    });
}

// ----- 3. Подтверждение удаления (модальное окно) -----
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-btn, .btn-delete');
    
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const itemName = this.getAttribute('data-name') || 'элемент';
            const message = `Вы уверены, что хотите удалить "${itemName}"?`;
            
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// ----- 4. Предпросмотр изображения перед загрузкой -----
function initImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            const previewId = this.getAttribute('data-preview') || 'image-preview';
            let preview = document.getElementById(previewId);
            
            if (!preview) {
                preview = document.createElement('img');
                preview.id = previewId;
                preview.style.maxWidth = '200px';
                preview.style.marginTop = '10px';
                preview.style.borderRadius = '8px';
                this.parentNode.appendChild(preview);
            }
            
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            
            reader.readAsDataURL(file);
        });
    });
}

// ----- 5. Валидация форм на клиенте -----
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// ----- 6. Автоматическая генерация slug из названия -----
function initAutoSlug() {
    const nameInput = document.getElementById('name');
    const slugInput = document.getElementById('slug');
    
    if (nameInput && slugInput) {
        nameInput.addEventListener('blur', function() {
            if (!slugInput.value || slugInput.value === '') {
                let slug = nameInput.value
                    .toLowerCase()
                    .replace(/[^а-яёa-z0-9]/g, '-')
                    .replace(/-+/g, '-')
                    .replace(/^-|-$/g, '');
                slugInput.value = slug;
            }
        });
    }
}

// ----- 7. Датапикеры (для фильтров) -----
function initDatePickers() {
    const dateInputs = document.querySelectorAll('.datepicker');
    
    dateInputs.forEach(input => {
        if (typeof flatpickr !== 'undefined') {
            flatpickr(input, {
                dateFormat: 'Y-m-d',
                locale: 'ru'
            });
        }
    });
}

// ----- 8. Графики на дашборде -----
function initCharts() {
    // Чарт для заказов (есть элемент с id ordersChart)
    const ordersChartCanvas = document.getElementById('ordersChart');
    if (ordersChartCanvas && typeof Chart !== 'undefined') {
        new Chart(ordersChartCanvas, {
            type: 'line',
            data: {
                labels: ordersChartCanvas.dataset.labels?.split(',') || [],
                datasets: [{
                    label: 'Заказы',
                    data: ordersChartCanvas.dataset.values?.split(',') || [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
    
    // Чарт для выручки
    const revenueChartCanvas = document.getElementById('revenueChart');
    if (revenueChartCanvas && typeof Chart !== 'undefined') {
        new Chart(revenueChartCanvas, {
            type: 'bar',
            data: {
                labels: revenueChartCanvas.dataset.labels?.split(',') || [],
                datasets: [{
                    label: 'Выручка (₽)',
                    data: revenueChartCanvas.dataset.values?.split(',') || [],
                    backgroundColor: '#27ae60',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
}

// ----- 9. Уведомления -----
function initNotifications() {
    // Проверка новых заказов каждые 30 секунд
    if (document.querySelector('.check-new-orders')) {
        setInterval(checkNewOrders, 30000);
    }
}

function checkNewOrders() {
    fetch('/admin_panel/orders/check-new/')
        .then(response => response.json())
        .then(data => {
            if (data.new_orders > 0) {
                showNotification(`Поступило ${data.new_orders} новых заказов!`, 'info');
                updateBadge();
            }
        });
}

function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// ----- 10. Вспомогательные функции -----

// Получение CSRF токена из куки
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Обновление бейджа с количеством новых заказов
function updateBadge() {
    const badge = document.querySelector('.new-orders-badge');
    if (badge) {
        fetch('/admin_panel/orders/count-new/')
            .then(r => r.json())
            .then(data => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            });
    }
}

// ----- 11. Массовые действия (выбрать все) -----
function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('.select-item');
    checkboxes.forEach(checkbox => {
        checkbox.checked = source.checked;
    });
}

function getSelectedItems() {
    const selected = [];
    document.querySelectorAll('.select-item:checked').forEach(checkbox => {
        selected.push(checkbox.value);
    });
    return selected;
}

function bulkAction(action) {
    const selected = getSelectedItems();
    if (selected.length === 0) {
        showNotification('Выберите хотя бы один элемент', 'warning');
        return;
    }
    
    if (confirm(`Выполнить "${action}" для ${selected.length} элементов?`)) {
        // Отправка AJAX запроса
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action, items: selected })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

// Экспорт данных в Excel
function exportToExcel() {
    window.location.href = window.location.pathname + '?export=csv';
}

// ----- 12. Поиск с задержкой (debounce) -----
let searchTimeout;
function debounceSearch(input) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const searchParams = new URLSearchParams(window.location.search);
        searchParams.set('search', input.value);
        window.location.search = searchParams.toString();
    }, 500);
}

// ----- Мобильное меню с оверлеем -----
function initMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarCollapse');
    
    // Создаем оверлей
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
        });
    }
    
    // Закрыть при клике на оверлей
    overlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });
    
    // Закрыть при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// Вызови в DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    // ... остальные инициализации
});