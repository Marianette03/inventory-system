document.addEventListener('DOMContentLoaded', () => {
    console.log("INVENTORY_SYS v2.0 | ENHANCED EDITION - Active");

    // Initialize all interactive features
    initializeAlerts();
    initializeModals();
    initializeSearch();
    initializeTooltips();
    initializeKeyboardShortcuts();
    initializeRealTimeUpdates();

    // Flash message auto-hide
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(msg => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);
});

function initializeAlerts() {
    // Mark alerts as read when clicked
    const alertItems = document.querySelectorAll('.alert-item');
    alertItems.forEach(item => {
        item.addEventListener('click', function() {
            const alertId = this.dataset.alertId;
            if (alertId) {
                markAlertRead(alertId);
                this.style.opacity = '0.5';
            }
        });
    });
}

function markAlertRead(alertId) {
    fetch(`/api/alerts/mark-read/${alertId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const alertItem = document.querySelector(`.alert-item[data-alert-id="${alertId}"]`);
            if (alertItem) {
                alertItem.remove();
            }

            const countEl = document.querySelector('.alert-count');
            if (countEl) {
                const currentCount = parseInt(countEl.textContent || '0', 10);
                countEl.textContent = Math.max(0, currentCount - 1);
            }

            showNotification('Alert dismissed.', 'success');
        } else {
            showNotification('Unable to dismiss alert.', 'error');
        }
    })
    .catch(error => {
        console.error('Error marking alert as read:', error);
        showNotification('Error dismissing alert.', 'error');
    });
}

function initializeModals() {
    // Modal functionality
    const modals = document.querySelectorAll('.modal');
    const closeBtns = document.querySelectorAll('.modal-close');

    closeBtns.forEach(btn => {
        btn.onclick = function() {
            modals.forEach(modal => modal.style.display = 'none');
        }
    });

    window.onclick = function(event) {
        modals.forEach(modal => {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        });
    });

    // ESC key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            modals.forEach(modal => modal.style.display = 'none');
        }
    });
}

function initializeSearch() {
    // Real-time search functionality
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-submit search forms
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    });
}

function initializeTooltips() {
    // Add tooltips to action buttons
    const actionButtons = document.querySelectorAll('.btn-icon, .action-buttons i');
    actionButtons.forEach(btn => {
        if (!btn.title) {
            const iconClass = btn.querySelector('i')?.className || btn.className;
            if (iconClass.includes('edit')) btn.title = 'Edit';
            else if (iconClass.includes('trash')) btn.title = 'Delete';
            else if (iconClass.includes('transfer')) btn.title = 'Adjust Stock';
            else if (iconClass.includes('eye')) btn.title = 'View Details';
        }
    });
}

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + F for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Ctrl/Cmd + N for new item
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('.btn-primary[href*="add"]') ||
                            document.querySelector('button[onclick*="showAddForm"]');
            if (addButton) {
                if (addButton.onclick) {
                    addButton.onclick();
                } else if (addButton.href) {
                    window.location.href = addButton.href;
                }
            }
        }

        // Ctrl/Cmd + R for refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            window.location.reload();
        }
    });
}

function initializeRealTimeUpdates() {
    // Auto-refresh dashboard data every 30 seconds
    if (window.location.pathname === '/dashboard') {
        setInterval(() => {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => {
                    updateDashboardStats(data);
                })
                .catch(error => console.error('Error updating dashboard:', error));
        }, 30000);
    }
}

function updateDashboardStats(data) {
    // Update stat cards with real-time data
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        const statValue = card.querySelector('.stat-value');
        if (statValue) {
            if (card.textContent.includes('Total Products')) {
                statValue.textContent = data.total_products;
            } else if (card.textContent.includes('Active Alerts')) {
                statValue.textContent = data.total_alerts;
                if (data.total_alerts > 0) {
                    statValue.style.color = '#ff4d4d';
                }
            } else if (card.textContent.includes('Low Stock')) {
                statValue.textContent = data.low_stock_count;
                if (data.low_stock_count > 0) {
                    statValue.style.color = '#ffa500';
                }
            }
        }
    });
}

// Barcode scanning functionality
function initializeBarcodeScanner() {
    let scanning = false;

    document.addEventListener('keydown', function(e) {
        if (scanning) return;

        // Start scanning on any key press when barcode input is focused
        const barcodeInput = document.querySelector('input[name="barcode"]');
        if (barcodeInput && document.activeElement === barcodeInput) {
            scanning = true;
            let barcode = '';

            const scanHandler = function(e) {
                if (e.key === 'Enter') {
                    document.removeEventListener('keydown', scanHandler);
                    scanning = false;

                    // Validate barcode format (12-13 digits)
                    if (/^\d{12,13}$/.test(barcode)) {
                        barcodeInput.value = barcode;
                        // Auto-fetch product data if on inventory page
                        if (window.location.pathname.includes('inventory')) {
                            fetchProductByBarcode(barcode);
                        }
                    }
                    barcode = '';
                } else if (e.key.length === 1) {
                    barcode += e.key;
                } else if (e.key === 'Escape') {
                    document.removeEventListener('keydown', scanHandler);
                    scanning = false;
                    barcode = '';
                }
            };

            document.addEventListener('keydown', scanHandler);

            // Timeout after 5 seconds
            setTimeout(() => {
                if (scanning) {
                    document.removeEventListener('keydown', scanHandler);
                    scanning = false;
                }
            }, 5000);
        }
    });
}

function fetchProductByBarcode(barcode) {
    fetch(`/api/barcode/${barcode}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Fill form with product data
                const product = data.product;
                Object.keys(product).forEach(key => {
                    const input = document.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = product[key] || '';
                    }
                });
                showNotification('Product data loaded from barcode', 'success');
            } else {
                showNotification('Product not found for this barcode', 'warning');
            }
        })
        .catch(error => {
            console.error('Error fetching product:', error);
            showNotification('Error scanning barcode', 'error');
        });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.innerHTML = `
        <i class='bx bx-${type === 'success' ? 'check' : type === 'error' ? 'x' : 'info'}-circle'></i>
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    const container = document.querySelector('.flash-messages') || document.body;
    container.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Enhanced table interactions
function initializeTableInteractions() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        // Row highlighting
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(0, 255, 136, 0.1)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.background = '';
            });
        });

        // Sortable headers
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, index);
            });
        });
    });
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();

        // Numeric sort for numbers
        if (!isNaN(aVal) && !isNaN(bVal)) {
            return parseFloat(aVal) - parseFloat(bVal);
        }

        return aVal.localeCompare(bVal);
    });

    rows.forEach(row => tbody.appendChild(row));
}

// Initialize barcode scanner
initializeBarcodeScanner();

// Initialize table interactions
initializeTableInteractions();

// Export functionality
function exportToCSV(filename, data) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Print functionality
function printSection(selector) {
    const printContent = document.querySelector(selector);
    const originalContent = document.body.innerHTML;

    document.body.innerHTML = printContent.outerHTML;
    window.print();
    document.body.innerHTML = originalContent;
}

// Lazy loading for large tables
function initializeLazyLoading() {
    const tables = document.querySelectorAll('.table-container table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        if (rows.length > 50) {
            // Implement pagination for large datasets
            paginateTable(table, 25);
        }
    });
}

function paginateTable(table, pageSize) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const totalPages = Math.ceil(rows.length / pageSize);

    // Create pagination controls
    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    pagination.innerHTML = `
        <button class="btn-secondary" onclick="changePage(-1)">Previous</button>
        <span id="page-info">Page 1 of ${totalPages}</span>
        <button class="btn-secondary" onclick="changePage(1)">Next</button>
    `;

    table.parentNode.appendChild(pagination);

    let currentPage = 0;
    showPage(currentPage);

    window.changePage = function(direction) {
        currentPage += direction;
        if (currentPage < 0) currentPage = 0;
        if (currentPage >= totalPages) currentPage = totalPages - 1;
        showPage(currentPage);
    };

    function showPage(page) {
        const start = page * pageSize;
        const end = start + pageSize;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });

        document.getElementById('page-info').textContent = `Page ${page + 1} of ${totalPages}`;
    }
}

// Delete Product functionality
function deleteProduct(productId, productName) {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        document.getElementById('deleteProductName').textContent = productName;
        document.getElementById('deleteForm').action = `/inventory/delete/${productId}`;
        modal.style.display = 'flex';
    }
}

// Supplier Modal Functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function viewSupplier(id, name, contact, email, phone, address) {
    document.getElementById('view_name').textContent = name || 'N/A';
    document.getElementById('view_contact').textContent = contact || 'N/A';
    document.getElementById('view_email').textContent = email || 'N/A';
    document.getElementById('view_phone').textContent = phone || 'N/A';
    document.getElementById('view_address').textContent = address || 'N/A';
    showModal('viewModal');
}

function editSupplier(id, name, contact, email, phone, address) {
    const form = document.getElementById('editForm');
    if (form) {
        form.action = `/suppliers/edit/${id}`;
        document.getElementById('edit_name').value = name;
        document.getElementById('edit_contact').value = contact;
        document.getElementById('edit_email').value = email;
        document.getElementById('edit_phone').value = phone;
        document.getElementById('edit_address').value = address;
        showModal('editModal');
    }
}

function deleteSupplier(id, name) {
    document.getElementById('supplierName').textContent = name;
    document.getElementById('deleteForm').action = `/suppliers/delete/${id}`;
    showModal('deleteModal');
}

// Category Modal Functions
function showAddForm() {
    const form = document.getElementById('addForm');
    if (form) form.style.display = 'block';
}

function hideAddForm() {
    const form = document.getElementById('addForm');
    if (form) form.style.display = 'none';
}

function editCategory(id, name, description) {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');
    if (form && modal) {
        form.action = `/categories/${id}`;
        document.getElementById('editName').value = name;
        document.getElementById('editDesc').value = description;
        modal.style.display = 'flex';
    }
}

function deleteCategory(id, name, count) {
    if (count > 0) {
        alert(`Cannot delete category "${name}" because it has ${count} product(s).`);
        return;
    }
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    if (modal && form) {
        document.getElementById('deleteName').textContent = name;
        form.action = `/categories/delete/${id}`;
        modal.style.display = 'flex';
    }
}

// Units Modal Functions
function editUnit(id, name, abbr) {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');
    if (form && modal) {
        form.action = `/units/${id}`;
        document.getElementById('editName').value = name;
        document.getElementById('editAbbr').value = abbr;
        modal.style.display = 'flex';
    }
}

function deleteUnit(id, name, count) {
    if (count > 0) {
        alert(`Cannot delete unit "${name}" because it has ${count} product(s).`);
        return;
    }
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    if (modal && form) {
        document.getElementById('deleteName').textContent = name;
        form.action = `/units/delete/${id}`;
        modal.style.display = 'flex';
    }
}

// Close modal on close button and outside click
document.addEventListener('DOMContentLoaded', function() {
    // Setup modal close buttons
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    // Close modal on outside click
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
});

// Initialize lazy loading
initializeLazyLoading();

console.log("All systems initialized successfully!");