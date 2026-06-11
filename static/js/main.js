document.addEventListener('DOMContentLoaded', function () {

    /* ---------------------------------------------------------------
       Mobile nav toggle
    ------------------------------------------------------------------ */
    var navToggle = document.getElementById('navToggle');
    var mobileNav = document.getElementById('mobileNav');
    if (navToggle && mobileNav) {
        navToggle.addEventListener('click', function () {
            mobileNav.classList.toggle('is-open');
        });
    }

    /* ---------------------------------------------------------------
       Dismiss flash messages
    ------------------------------------------------------------------ */
    document.querySelectorAll('.flash__close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var flash = btn.closest('.flash');
            if (flash) {
                flash.style.transition = 'opacity 0.2s ease';
                flash.style.opacity = '0';
                setTimeout(function () { flash.remove(); }, 200);
            }
        });
    });

    /* Auto-dismiss flashes after 6s */
    setTimeout(function () {
        document.querySelectorAll('.flash').forEach(function (flash) {
            flash.style.transition = 'opacity 0.3s ease';
            flash.style.opacity = '0';
            setTimeout(function () { flash.remove(); }, 300);
        });
    }, 6000);

    /* ---------------------------------------------------------------
       Password show/hide toggles
    ------------------------------------------------------------------ */
    document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.getAttribute('data-toggle-password');
            var input = document.getElementById(targetId);
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = 'Hide';
            } else {
                input.type = 'password';
                btn.textContent = 'Show';
            }
        });
    });

    /* ---------------------------------------------------------------
       Cascading manufacturer -> model dropdown
    ------------------------------------------------------------------ */
    var companySelect = document.getElementById('company');
    var modelSelect = document.getElementById('car_model');

    if (companySelect && modelSelect && window.COMPANY_MODELS_URL) {

        function loadModels(company, preselect) {
            modelSelect.innerHTML = '';
            if (!company) {
                modelSelect.disabled = true;
                var placeholder = document.createElement('option');
                placeholder.value = '';
                placeholder.textContent = 'Select manufacturer first';
                placeholder.disabled = true;
                placeholder.selected = true;
                modelSelect.appendChild(placeholder);
                return;
            }

            var url = window.COMPANY_MODELS_URL.replace('__COMPANY__', encodeURIComponent(company));

            var loadingOpt = document.createElement('option');
            loadingOpt.value = '';
            loadingOpt.textContent = 'Loading models…';
            loadingOpt.disabled = true;
            loadingOpt.selected = true;
            modelSelect.appendChild(loadingOpt);
            modelSelect.disabled = true;

            fetch(url)
                .then(function (res) { return res.json(); })
                .then(function (models) {
                    modelSelect.innerHTML = '';

                    var placeholder = document.createElement('option');
                    placeholder.value = '';
                    placeholder.textContent = 'Select model';
                    placeholder.disabled = true;
                    placeholder.selected = !preselect;
                    modelSelect.appendChild(placeholder);

                    models.forEach(function (m) {
                        var opt = document.createElement('option');
                        opt.value = m;
                        opt.textContent = m;
                        if (preselect && m === preselect) {
                            opt.selected = true;
                        }
                        modelSelect.appendChild(opt);
                    });

                    modelSelect.disabled = false;
                })
                .catch(function () {
                    modelSelect.innerHTML = '';
                    var errOpt = document.createElement('option');
                    errOpt.value = '';
                    errOpt.textContent = 'Could not load models';
                    errOpt.disabled = true;
                    errOpt.selected = true;
                    modelSelect.appendChild(errOpt);
                });
        }

        companySelect.addEventListener('change', function () {
            loadModels(companySelect.value, null);
        });

        // On page load, if a company was already selected (e.g. validation
        // error round-trip), repopulate the model dropdown and re-select.
        if (companySelect.value) {
            var preselect = modelSelect.getAttribute('data-selected') || null;
            loadModels(companySelect.value, preselect);
        }
    }

    /* ---------------------------------------------------------------
       Result gauge animation
    ------------------------------------------------------------------ */
    var readoutCard = document.getElementById('readoutCard');
    var gaugeValue = document.getElementById('gaugeValue');
    var gaugeArc = document.getElementById('gaugeArc');
    var gaugeNeedle = document.getElementById('gaugeNeedle');

    if (readoutCard && gaugeValue) {
        var price = parseFloat(readoutCard.getAttribute('data-price'));
        if (!isNaN(price)) {
            var MAX_REFERENCE = 2000000; // ₹20,00,000 — gauge full-scale reference
            var ratio = Math.max(0, Math.min(1, price / MAX_REFERENCE));

            // Arc fill
            var ARC_LENGTH = 314; // approx length of the semicircle path
            if (gaugeArc) {
                requestAnimationFrame(function () {
                    gaugeArc.style.strokeDashoffset = (ARC_LENGTH * (1 - ratio)).toFixed(1);
                });
            }

            // Needle rotation: -90deg (left) at ratio 0, +90deg (right) at ratio 1
            if (gaugeNeedle) {
                var angle = -90 + ratio * 180;
                requestAnimationFrame(function () {
                    gaugeNeedle.style.transform = 'rotate(' + angle + 'deg)';
                });
            }

            // Animated count-up
            var duration = 1000;
            var start = null;
            function step(timestamp) {
                if (!start) start = timestamp;
                var progress = Math.min((timestamp - start) / duration, 1);
                var current = Math.floor(progress * price);
                gaugeValue.textContent = current.toLocaleString('en-IN');
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    gaugeValue.textContent = Math.round(price).toLocaleString('en-IN');
                }
            }
            requestAnimationFrame(step);
        }
    }
});
