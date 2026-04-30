document.addEventListener('DOMContentLoaded', function () {
    // 1. Fix layering between top-bar dropdowns and offcanvas sidebar
    const topBar = document.getElementById('topAnnouncementBar');
    const offcanvasEl = document.getElementById('offcanvasNavbar');
    if (topBar && offcanvasEl) {
        offcanvasEl.addEventListener('show.bs.offcanvas', () => {
            topBar.style.zIndex = '1010'; // Send behind offcanvas
        });
        offcanvasEl.addEventListener('hidden.bs.offcanvas', () => {
            topBar.style.zIndex = '1030'; // Bring back to front for dropdowns
        });
    }

    // 2. Wishlist Forms Logic
    const wishlistForms = document.querySelectorAll('.wishlist-form');
    wishlistForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const url = this.action;
            const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
            const heartIcon = this.querySelector('.fa-heart');
            const heartContainer = this.querySelector('.shop-card-heart');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'added') {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                        heartContainer.classList.add('text-danger');
                    } else if (data.status === 'removed') {
                        heartIcon.classList.remove('fas');
                        heartIcon.classList.add('far');
                        heartContainer.classList.remove('text-danger');

                        if (window.location.pathname.includes('wishlist')) {
                            const cardCol = this.closest('.col');
                            if (cardCol) {
                                cardCol.remove();
                                if (document.querySelectorAll('.shop-card').length === 0) {
                                    window.location.reload();
                                }
                            }
                        }
                    }
                })
                .catch(error => console.error('Error updating wishlist:', error));
        });
    });

    // 3. Language Selector Load
    const savedLang = localStorage.getItem('selectedLang');
    if (savedLang) {
        document.getElementById('langLabel').innerHTML = savedLang;
    }

    // 4. AJAX Cart Update (Add/Remove)
    document.body.addEventListener('click', function(e) {
        const target = e.target.closest('a.ajax-cart-update');
        if (target) {
            e.preventDefault();
            fetch(target.href, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    let hoverCartContent = document.getElementById('hover-cart-content');
                    if (hoverCartContent && data.cart_html) {
                        hoverCartContent.innerHTML = data.cart_html;
                    }
                    
                    let cartIcon = document.querySelector('.fa-shopping-cart');
                    if (cartIcon) {
                        let badge = cartIcon.nextElementSibling;
                        if (badge && badge.classList.contains('badge')) {
                            badge.innerText = data.cart_count;
                            if (data.cart_count === 0) badge.remove();
                        } else if (data.cart_count > 0) {
                            let newBadge = document.createElement('span');
                            newBadge.className = 'position-absolute top-0 start-100 translate-middle badge cart-badge bg-danger';
                            newBadge.innerText = data.cart_count;
                            cartIcon.parentNode.appendChild(newBadge);
                        }
                    }
                } else if (data.status === 'error') {
                    alert(data.message);
                }
            });
        }
    });

    document.body.addEventListener('submit', function(e) {
        const form = e.target.closest('form.ajax-cart-remove');
        if (form) {
            e.preventDefault();
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    let hoverCartContent = document.getElementById('hover-cart-content');
                    if (hoverCartContent && data.cart_html) {
                        hoverCartContent.innerHTML = data.cart_html;
                    }
                    
                    let cartIcon = document.querySelector('.fa-shopping-cart');
                    if (cartIcon) {
                        let badge = cartIcon.nextElementSibling;
                        if (badge && badge.classList.contains('badge')) {
                            badge.innerText = data.cart_count;
                            if (data.cart_count === 0) badge.remove();
                        } else if (data.cart_count > 0) {
                            let newBadge = document.createElement('span');
                            newBadge.className = 'position-absolute top-0 start-100 translate-middle badge cart-badge bg-danger';
                            newBadge.innerText = data.cart_count;
                            cartIcon.parentNode.appendChild(newBadge);
                        }
                    }
                }
            });
        }
    });

    // 5. Typeahead Inputs
    const typeaheadInputs = document.querySelectorAll('.typeahead-input');
    typeaheadInputs.forEach(input => {
        const container = input.closest('.typeahead-container');
        const dropdown = container.querySelector('.typeahead-dropdown');
        const loaderWrapper = container.querySelector('.typeahead-loader');
        const resultsContainer = container.querySelector('.typeahead-results');
        const searchUrl = input.getAttribute('data-search-url');
        let debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length === 0) {
                dropdown.style.display = 'none';
                return;
            }

            dropdown.style.display = 'block';
            loaderWrapper.style.setProperty('display', 'flex', 'important');
            resultsContainer.innerHTML = '';

            debounceTimer = setTimeout(() => {
                fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        loaderWrapper.style.setProperty('display', 'none', 'important');
                        resultsContainer.innerHTML = '';
                        
                        if (data.results.length === 0) {
                            resultsContainer.innerHTML = '<div class="p-3 text-muted text-center small">No results found</div>';
                            return;
                        }

                        data.results.forEach(item => {
                            const a = document.createElement('a');
                            a.href = item.url;
                            a.className = 'result-item';
                            
                            let html = '';
                            if (item.image_url) {
                                html += `<img src="${item.image_url}" style="width: 40px; height: 40px; object-fit: contain; margin-right: 10px;" class="rounded border bg-white">`;
                            } else if (item.status) {
                                html += `<div class="rounded bg-light text-muted d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;"><i class="fas fa-box"></i></div>`;
                            } else if (item.username) {
                                html += `<div class="rounded bg-light text-muted d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;"><i class="fas fa-user"></i></div>`;
                            } else {
                                html += `<div class="rounded bg-light text-muted d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;"><i class="fas fa-image"></i></div>`;
                            }
                            
                            html += `<div class="d-flex flex-column" style="min-width: 0;">`;
                            if (item.price) {
                                html += `<span class="fw-bold text-truncate" style="font-size: 0.9rem;">${item.name}</span>`;
                                html += `<span class="text-primary fw-bold" style="font-size: 0.8rem;">₱${item.price}</span>`;
                            } else if (item.status) {
                                html += `<span class="fw-bold" style="font-size: 0.9rem;">Order #${item.id}</span>`;
                                html += `<span class="text-muted text-truncate" style="font-size: 0.8rem;">${item.customer} • ${item.status}</span>`;
                            } else if (item.username) {
                                html += `<span class="fw-bold text-truncate" style="font-size: 0.9rem;">${item.name}</span>`;
                                html += `<span class="text-muted" style="font-size: 0.8rem;">${item.student_id}</span>`;
                            }
                            html += `</div>`;
                            
                            a.innerHTML = html;
                            resultsContainer.appendChild(a);
                        });
                    })
                    .catch(err => {
                        loaderWrapper.style.setProperty('display', 'none', 'important');
                        resultsContainer.innerHTML = '<div class="p-3 text-danger text-center small">Error loading results</div>';
                    });
            }, 400); // 400ms debounce
        });

        document.addEventListener('click', function(e) {
            if (!container.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
        
        input.addEventListener('focus', function() {
            if (this.value.trim().length > 0) {
                dropdown.style.display = 'block';
            }
        });
    });
});

// Global Function outside DOMContentLoaded
function changeLang(lang, langCode) {
    localStorage.setItem('selectedLang', lang);
    localStorage.setItem('selectedLangCode', langCode);
    document.getElementById('langLabel').innerHTML = lang;
    
    // Set Google Translate cookie
    if (langCode === 'en') {
        document.cookie = `googtrans=/en/en; path=/`;
        document.cookie = `googtrans=/en/en; domain=.${window.location.hostname}; path=/`;
    } else {
        document.cookie = `googtrans=/en/${langCode}; path=/`;
        document.cookie = `googtrans=/en/${langCode}; domain=.${window.location.hostname}; path=/`;
    }
    window.location.reload();
}
