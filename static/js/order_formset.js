/**
 * Bunai Dynamic Inline Formset & Financial Calculator
 * Handles dynamic product addition/deletion, stock checking, and live total calculations.
 */

document.addEventListener('DOMContentLoaded', function () {
  const formsetContainer = document.getElementById('order-items-formset-container');
  const addRowBtn = document.getElementById('add-item-row-btn');
  const totalFormsInput = document.getElementById('id_items-TOTAL_FORMS');
  const emptyTemplate = document.getElementById('empty-form-template');
  
  // Financial summary elements
  const subtotalDisplay = document.getElementById('calc-subtotal-display');
  const discountInput = document.getElementById('id_discount_amount');
  const taxRateInput = document.getElementById('id_tax_rate_percent');
  const taxAmountDisplay = document.getElementById('calc-tax-display');
  const shippingInput = document.getElementById('id_shipping_fee');
  const grandTotalDisplay = document.getElementById('calc-grand-total-display');
  const totalItemsDisplay = document.getElementById('calc-total-items-display');

  // Load product catalog data if available
  let catalog = {};
  const catalogScript = document.getElementById('products-catalog-data');
  if (catalogScript && catalogScript.textContent) {
    try {
      catalog = JSON.parse(catalogScript.textContent);
    } catch (e) {
      console.error('Error parsing product catalog data', e);
    }
  }

  // Recalculate full order financial summary
  function calculateOrderSummary() {
    let subtotal = 0;
    let totalItems = 0;

    const rows = formsetContainer.querySelectorAll('.formset-item-row');
    rows.forEach(function (row) {
      const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
      if (deleteCheckbox && deleteCheckbox.checked) {
        return; // Skip deleted forms
      }
      if (row.style.display === 'none') {
        return;
      }

      const productSelect = row.querySelector('.order-product-select');
      const qtyInput = row.querySelector('.order-quantity-input');
      const priceInput = row.querySelector('.order-price-input');
      const lineTotalDisplay = row.querySelector('.line-total-display');
      const stockHint = row.querySelector('.stock-availability-hint');

      const qty = parseFloat(qtyInput ? qtyInput.value : 0) || 0;
      const price = parseFloat(priceInput ? priceInput.value : 0) || 0;
      const lineTotal = qty * price;

      if (lineTotalDisplay) {
        lineTotalDisplay.textContent = '₹' + lineTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      }

      if (productSelect && productSelect.value && catalog[productSelect.value] && stockHint) {
        const prod = catalog[productSelect.value];
        if (prod.stock <= 0) {
          stockHint.innerHTML = '<span class="badge bg-danger">Out of stock (' + prod.stock + ')</span>';
        } else if (prod.stock <= 5) {
          stockHint.innerHTML = '<span class="badge bg-warning text-dark">Low stock (' + prod.stock + ' ' + prod.unit + ')</span>';
        } else {
          stockHint.innerHTML = '<span class="badge bg-success">In stock (' + prod.stock + ' ' + prod.unit + ')</span>';
        }
      }

      if (qty > 0) {
        subtotal += lineTotal;
        totalItems += qty;
      }
    });

    const discount = parseFloat(discountInput ? discountInput.value : 0) || 0;
    const taxRate = parseFloat(taxRateInput ? taxRateInput.value : 0) || 0;
    const shipping = parseFloat(shippingInput ? shippingInput.value : 0) || 0;

    const taxableBase = Math.max(0, subtotal - discount);
    const taxAmount = (taxableBase * taxRate) / 100.0;
    const grandTotal = Math.max(0, taxableBase + taxAmount + shipping);

    if (subtotalDisplay) {
      subtotalDisplay.textContent = '₹' + subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    if (taxAmountDisplay) {
      taxAmountDisplay.textContent = '₹' + taxAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    if (grandTotalDisplay) {
      grandTotalDisplay.textContent = '₹' + grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    if (totalItemsDisplay) {
      totalItemsDisplay.textContent = totalItems.toString();
    }
  }

  // Attach event listeners to a specific row
  function attachRowListeners(row) {
    const productSelect = row.querySelector('.order-product-select');
    const qtyInput = row.querySelector('.order-quantity-input');
    const priceInput = row.querySelector('.order-price-input');
    const removeBtn = row.querySelector('.remove-formset-row-btn');
    const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');

    if (productSelect) {
      productSelect.addEventListener('change', function () {
        const prodId = this.value;
        if (prodId && catalog[prodId]) {
          const prod = catalog[prodId];
          if (priceInput && (!priceInput.value || priceInput.value === '0' || priceInput.value === '0.00')) {
            priceInput.value = prod.price.toFixed(2);
          }
        }
        calculateOrderSummary();
      });
    }

    if (qtyInput) {
      qtyInput.addEventListener('input', calculateOrderSummary);
    }

    if (priceInput) {
      priceInput.addEventListener('input', calculateOrderSummary);
    }

    if (removeBtn) {
      removeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (deleteCheckbox) {
          // If existing instance, mark for deletion
          deleteCheckbox.checked = true;
          row.style.display = 'none';
          row.classList.add('is-deleted');
        } else {
          // Newly added uncommitted row, simply remove DOM element
          row.remove();
        }
        calculateOrderSummary();
      });
    }
  }

  // Initialize all existing rows
  if (formsetContainer) {
    const rows = formsetContainer.querySelectorAll('.formset-item-row');
    rows.forEach(attachRowListeners);
  }

  // Handle Add Item Row Button
  if (addRowBtn && emptyTemplate && totalFormsInput) {
    addRowBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const currentFormCount = parseInt(totalFormsInput.value, 10);
      const newHtml = emptyTemplate.innerHTML.replace(/__prefix__/g, currentFormCount);
      
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = newHtml.trim();
      const newRow = tempDiv.firstElementChild;
      
      formsetContainer.appendChild(newRow);
      totalFormsInput.value = currentFormCount + 1;
      
      attachRowListeners(newRow);
      calculateOrderSummary();
    });
  }

  // Attach listeners to global financial inputs
  if (discountInput) discountInput.addEventListener('input', calculateOrderSummary);
  if (taxRateInput) taxRateInput.addEventListener('input', calculateOrderSummary);
  if (shippingInput) shippingInput.addEventListener('input', calculateOrderSummary);

  // Initial calculation
  calculateOrderSummary();
});
