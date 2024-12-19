// static/js/product_list.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrfToken = getCookie('csrftoken');

    // UOM Mappings for JavaScript
    const uomMappings = {
        'Tablet': ['Pieces'],
        'Capsule': ['Pieces'],
        'Powder': ['Grams', 'Kilograms'],
        'Liquid': ['ml', 'Liters'],
        'Syrup': ['ml', 'Grams'],
        'Cream': ['Grams'],
        'Leaves': ['Grams'],
        'Other': ['Custom'],  // Allow any UOM for 'Other'
    };

    // Function to update UOM options based on selected content_type
    function updateUomOptions(selectedContentType, selectedUom = null) {
        const options = uomMappings[selectedContentType] || [];
        const uomSelect = document.querySelector('select[name="uom"]');
        if (!uomSelect) return;

        // Clear existing options
        uomSelect.innerHTML = '<option value="">Select Unit</option>';

        // Populate new options
        options.forEach(uom => {
            const option = document.createElement('option');
            option.value = uom;
            option.textContent = uom;
            if (uom === selectedUom) {
                option.selected = true;
            }
            uomSelect.appendChild(option);
        });

        // Enable or disable UOM based on availability
        uomSelect.disabled = options.length === 0;
    }

    // Attach event listener to the Content Type dropdown
    const contentTypeField = document.getElementById('content_type');
    if (contentTypeField) {
        contentTypeField.addEventListener('change', function() {
            const selectedContentType = contentTypeField.value;
            updateUomOptions(selectedContentType);
        });
    }

    // Modal elements
    const openModalButton = document.getElementById('openModalButton');
    const modal = document.getElementById('modal');
    const closeModalButtons = document.querySelectorAll('#closeModalButton, #closeModalButtonFooter');
    const productForm = document.getElementById('productForm');
    const modalTitle = document.getElementById('modalTitle');
    const submitButton = document.getElementById('submitButton');

    let isEditMode = false;
    let editProductId = null;

    // Debounce function to limit the rate of function calls
    function debounce(func, delay) {
        let debounceTimer;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        };
    }

    // Open modal for adding new product
    if (openModalButton) {
        openModalButton.addEventListener('click', () => {
            resetForm();
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        });
    }

    // Close modal
    closeModalButtons.forEach(button => {
        button.addEventListener('click', () => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            resetForm();
        });
    });

    // Close modal when clicking outside the modal content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            resetForm();
        }
    });

    // Reset form to default (add mode)
    function resetForm() {
        isEditMode = false;
        editProductId = null;
        productForm.reset();
        productForm.action = URLs.add_product;
        modalTitle.textContent = "Add New Product";
        submitButton.textContent = "Save Product";
        // Re-enable and hide linked_article and custom_content_type fields if they were disabled
        const linkedArticleContainer = document.getElementById('linkedArticleContainer');
        const linkedArticleField = productForm.querySelector('select[name="linked_article"]');
        if (linkedArticleContainer) {
            linkedArticleContainer.classList.add('hidden');
            linkedArticleField.disabled = true;
            linkedArticleField.innerHTML = '<option value="">Select Article</option>'; // Clear options
        }
        const customContentTypeContainer = document.getElementById('customContentTypeContainer');
        const customContentTypeField = productForm.querySelector('input[name="custom_content_type"]');
        if (customContentTypeContainer) {
            customContentTypeContainer.classList.add('hidden');
            customContentTypeField.disabled = true;
            customContentTypeField.value = ''; // Clear the field
        }
        // Reset UOM options based on default or existing selection
        const contentTypeSelect = productForm.querySelector('select[name="content_type"]');
        const selectedContentType = contentTypeSelect.value;
        updateUomOptions(selectedContentType);
        // Reset quantity field
        const quantityInput = productForm.querySelector('input[name="quantity"]');
        if (quantityInput) {
            quantityInput.value = '';
        }
    }

    // Handle 'Select All' checkbox
    const selectAllCheckbox = document.getElementById('checkbox-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            let checkboxes = document.querySelectorAll('input[name="product_ids"]');
            checkboxes.forEach((checkbox) => {
                checkbox.checked = this.checked;
            });
        });
    }

    // Bulk delete functionality
    const bulkDeleteButton = document.getElementById('bulkDeleteButton');
    if (bulkDeleteButton) {
        bulkDeleteButton.addEventListener('click', function() {
            // Collect selected product IDs
            let checkboxes = document.querySelectorAll('input[name="product_ids"]:checked');
            if (checkboxes.length === 0) {
                Swal.fire(
                    'No products selected',
                    'Please select at least one product to delete.',
                    'warning'
                );
                return;
            }

            let productIds = [];
            checkboxes.forEach((checkbox) => {
                productIds.push(checkbox.value);
            });

            Swal.fire({
                title: 'Are you sure?',
                text: 'You will not be able to recover these products!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete them!'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Prepare form data
                    let formData = new FormData();
                    productIds.forEach((id) => {
                        formData.append('product_ids', id);
                    });
                    // Send AJAX request to bulk delete products
                    fetch(URLs.bulk_delete_products, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        credentials: 'same-origin',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            Swal.fire(
                                'Deleted!',
                                'Your selected products have been deleted.',
                                'success'
                            );
                            // Remove the deleted product rows from the table
                            productIds.forEach((productId) => {
                                let row = document.getElementById('product-row-' + productId);
                                if (row) {
                                    row.remove();
                                }
                            });
                            // Uncheck the 'Select All' checkbox
                            if (selectAllCheckbox) {
                                selectAllCheckbox.checked = false;
                            }
                        } else {
                            Swal.fire(
                                'Error!',
                                data.message || 'An error occurred.',
                                'error'
                            );
                        }
                    })
                    .catch((error) => {
                        Swal.fire(
                            'Error!',
                            'An error occurred.',
                            'error'
                        );
                    });
                }
            });
        });
    }

    // Individual delete functionality
    window.deleteProduct = function(productId) {
        Swal.fire({
            title: 'Are you sure?',
            text: 'You will not be able to recover this product!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                // Prepare form data
                let formData = new FormData();
                // Send AJAX request to delete product
                let deleteUrl = URLs.delete_product.replace('/0/', `/${productId}/`);
                fetch(deleteUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire(
                            'Deleted!',
                            'Your product has been deleted.',
                            'success'
                        );
                        // Remove the deleted product row from the table
                        let row = document.getElementById('product-row-' + productId);
                        if (row) {
                            row.remove();
                        }
                    } else {
                        Swal.fire(
                            'Error!',
                            data.message || 'An error occurred.',
                            'error'
                        );
                    }
                })
                .catch((error) => {
                    Swal.fire(
                        'Error!',
                        'An error occurred while deleting the product.',
                        'error'
                    );
                });
            }
        });
    }

    // Handle Image Click to Show in Modal
    function attachImageClickEvents() {
        document.querySelectorAll('.product-image').forEach(function(image) {
            image.addEventListener('click', function() {
                const fullImageUrl = this.getAttribute('data-full-url');
                const altText = this.getAttribute('alt');
                Swal.fire({
                    title: altText,
                    imageUrl: fullImageUrl,
                    imageAlt: altText,
                    showCloseButton: true,
                    showConfirmButton: false,
                    width: 'auto',
                    heightAuto: true,
                    customClass: {
                        popup: 'p-0 rounded-lg',
                        image: 'object-contain w-auto h-96' // Adjust size as needed
                    }
                });
            });
        });
    }

    attachImageClickEvents();

    // Edit Product Functionality
    window.editProduct = function(productId) {
        // Fetch product data via AJAX
        let editUrl = URLs.edit_product.replace('/0/', `/${productId}/`);
        fetch(editUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const product = data.product;
                // Populate form fields
                productForm.querySelector('input[name="item_name"]').value = product.item_name || '';
                productForm.querySelector('select[name="supplier"]').value = product.supplier_id || '';
                productForm.querySelector('input[name="currency_code"]').value = product.currency_code || '';
                productForm.querySelector('input[name="retail_price"]').value = product.retail_price || '';
                productForm.querySelector('select[name="uom"]').value = product.uom || '';
                productForm.querySelector('input[name="quantity"]').value = product.quantity || '';
                productForm.querySelector('select[name="product_type"]').value = product.product_type || ''; // Populate product_type
                productForm.querySelector('select[name="content_type"]').value = product.content_type || ''; // Populate content_type
                productForm.querySelector('input[name="custom_content_type"]').value = product.custom_content_type || '';
                productForm.querySelector('select[name="linked_article"]').value = product.linked_article_id || '';
                productForm.querySelector('input[name="discountable_all"]').checked = product.discountable_all === true;
                productForm.querySelector('input[name="discountable_members"]').checked = product.discountable_members === true;
                productForm.querySelector('input[name="active"]').checked = product.active === true;

                // Show or hide linked_article field based on product_type
                const linkedArticleContainer = document.getElementById('linkedArticleContainer');
                const linkedArticleField = productForm.querySelector('select[name="linked_article"]');
                if (product.product_type === 'Component') {
                    linkedArticleContainer.classList.remove('hidden');
                    linkedArticleField.disabled = false;
                    // Fetch and populate linked_article dropdown
                    populateLinkedArticles(product.linked_article_id);
                } else {
                    linkedArticleContainer.classList.add('hidden');
                    linkedArticleField.disabled = true;
                    linkedArticleField.innerHTML = '<option value="">Select Article</option>'; // Clear options
                }

                // Show or hide custom_content_type field based on content_type
                const customContentTypeContainer = document.getElementById('customContentTypeContainer');
                const customContentTypeField = productForm.querySelector('input[name="custom_content_type"]');
                if (product.content_type === 'Other') {
                    customContentTypeContainer.classList.remove('hidden');
                    customContentTypeField.disabled = false;
                    // Disable UOM if 'Other' should allow free-form UOM
                    updateUomOptions('Other', product.uom);
                    const uomSelect = productForm.querySelector('select[name="uom"]');
                    if (uomSelect) {
                        uomSelect.disabled = true;
                        uomSelect.value = ''; // Clear UOM if it's disabled
                    }
                } else {
                    customContentTypeContainer.classList.add('hidden');
                    customContentTypeField.disabled = true;
                    customContentTypeField.value = ''; // Clear custom content type input
                    // Update UOM options based on selected content_type
                    const selectedContentType = product.content_type;
                    updateUomOptions(selectedContentType, product.uom);
                }

                // Change form action to update_product
                productForm.action = URLs.update_product.replace('/0/', `/${productId}/`);
                // Update modal title and button text
                modalTitle.textContent = "Edit Product";
                submitButton.textContent = "Update Product";
                // Set edit mode flags
                isEditMode = true;
                editProductId = product.id;
                // Open modal
                modal.classList.remove('hidden');
                modal.classList.add('flex');

                // Update UOM options based on content_type
                const contentTypeSelect = productForm.querySelector('select[name="content_type"]');
                const selectedContentType = contentTypeSelect.value;
                updateUomOptions(selectedContentType, product.uom);
            } else {
                Swal.fire(
                    'Error!',
                    data.message || 'Failed to fetch product data.',
                    'error'
                );
            }
        })
        .catch((error) => {
            console.log('Error:', error);
            Swal.fire(
                'Error!',
                'An error occurred while fetching product data.',
                'error'
            );
        });
    }

    // Function to fetch and populate linked_article dropdown (with components)
async function populateLinkedArticles(selectedArticleId = null) {
    const linkedArticleContainer = document.getElementById('linkedArticleContainer');
    const linkedArticleField = productForm.querySelector('select[name="linked_article"]');

    // Show the container and enable the dropdown
    linkedArticleContainer.classList.remove('hidden');
    linkedArticleField.disabled = false;

    // Clear existing options and show loading message
    linkedArticleField.innerHTML = '<option value="">Loading components...</option>';

    try {
        // Fetch components (not articles) from the backend endpoint
        const response = await fetch('/get_linked_articles/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });

        // Check if response is successful (status code 200)
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const text = await response.text(); // Get response as text

        // Check if response is valid JSON
        try {
            const data = JSON.parse(text); // Attempt to parse JSON
            linkedArticleField.innerHTML = ''; // Clear the loading message

            // If there are components, populate the dropdown
            if (data.articles && data.articles.length > 0) {
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Select Component';
                linkedArticleField.appendChild(defaultOption);

                data.articles.forEach(component => {
                    const option = document.createElement('option');
                    option.value = component.id;
                    option.textContent = component.item_name;
                    if (selectedArticleId && component.id === selectedArticleId) {
                        option.selected = true;
                    }
                    linkedArticleField.appendChild(option);
                });
            } else {
                // If no components, show "No components available"
                const noOption = document.createElement('option');
                noOption.value = '';
                noOption.textContent = 'No components available.';
                linkedArticleField.appendChild(noOption);
            }
        } catch (parseError) {
            // If JSON parsing fails, log and show an error message
            console.error('Error parsing JSON:', parseError);
            linkedArticleField.innerHTML = ''; // Clear the loading message
            const errorOption = document.createElement('option');
            errorOption.value = '';
            errorOption.textContent = 'Error loading components (invalid data).';
            linkedArticleField.appendChild(errorOption);
        }
    } catch (error) {
        console.error('Error fetching components:', error);
        linkedArticleField.innerHTML = ''; // Clear the loading message
        const errorOption = document.createElement('option');
        errorOption.value = '';
        errorOption.textContent = 'Error loading components (network/server issue).';
        linkedArticleField.appendChild(errorOption);
    }
}



    // Handle form submission for adding and editing
    productForm.addEventListener('submit', function(event) {
        if (isEditMode && editProductId) {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(this);

            fetch(productForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire(
                        'Updated!',
                        data.message,
                        'success'
                    );
                    // Optionally, update the product row in the table with new data
                    const updatedProduct = data.product;
                    const row = document.getElementById('product-row-' + updatedProduct.id);
                    if (row) {
                        // Update Product Cell with Image and Name
                        row.querySelector('th[scope="row"]').innerHTML = `
                            ${updatedProduct.photo_url ? `
                                <img 
                                    src="${updatedProduct.photo_url}" 
                                    alt="${updatedProduct.item_name}" 
                                    class="w-8 h-8 mr-3 object-cover rounded product-image cursor-pointer" 
                                    data-full-url="${updatedProduct.photo_url}"
                                    title="Click to view full image"
                                >
                            ` : `
                                <img 
                                    src="${placeholderImageUrl}" 
                                    alt="${updatedProduct.item_name}" 
                                    class="w-8 h-8 mr-3 object-cover rounded product-image cursor-pointer" 
                                    data-full-url="${placeholderImageUrl}"
                                    title="Click to view full image"
                                >
                            `}
                            ${updatedProduct.item_name}  
                        `;
                        // Update Product Type
                        row.querySelector('td:nth-child(3)').textContent = updatedProduct.product_type_display;
                        // Update Content Type
                        row.querySelector('td:nth-child(4)').textContent = updatedProduct.content_type_display || 'N/A';
                        // Update Quantity
                        row.querySelector('td:nth-child(5)').textContent = updatedProduct.quantity;
                        // Update UOM
                        row.querySelector('td:nth-child(6)').textContent = updatedProduct.uom;
                        // Update Supplier
                        row.querySelector('td:nth-child(7)').textContent = updatedProduct.supplier_name;
                        // Update Currency
                        row.querySelector('td:nth-child(8)').textContent = updatedProduct.currency_code;
                        // Update Price
                        row.querySelector('td:nth-child(9)').textContent = `$${updatedProduct.retail_price}`;
                        // Update Discountable (All)
                        row.querySelector('td:nth-child(10)').textContent = updatedProduct.discountable_all ? 'Yes' : 'No';
                        // Update Discountable (Members)
                        row.querySelector('td:nth-child(11)').textContent = updatedProduct.discountable_members ? 'Yes' : 'No';
                        // Update Active
                        row.querySelector('td:nth-child(12)').textContent = updatedProduct.active ? 'Yes' : 'No';
                        // Update Sellable Sets
                        row.querySelector('td:nth-child(13)').textContent = updatedProduct.product_type === 'Article' ? updatedProduct.sellable_sets : 'N/A';

                        // Re-attach event listener for the new image
                        const productImage = row.querySelector('.product-image');
                        if (productImage) {
                            productImage.addEventListener('click', function() {
                                const fullImageUrl = this.getAttribute('data-full-url');
                                const altText = this.getAttribute('alt');
                                Swal.fire({
                                    title: altText,
                                    imageUrl: fullImageUrl,
                                    imageAlt: altText,
                                    showCloseButton: true,
                                    showConfirmButton: false,
                                    width: 'auto',
                                    heightAuto: true,
                                    customClass: {
                                        popup: 'p-0 rounded-lg',
                                        image: 'object-contain w-auto h-96' // Adjust size as needed
                                    }
                                });
                            });
                        }
                    }
                    // Close modal and reset form
                    modal.classList.add('hidden');
                    modal.classList.remove('flex');
                    resetForm();
                } else {
                    // Handle form errors
                    if (data.errors) {
                        let errorMessages = '';
                        const errors = JSON.parse(data.errors);
                        for (let field in errors) {
                            errors[field].forEach(error => {
                                errorMessages += `${error.message}<br>`;
                            });
                        }
                        Swal.fire({
                            icon: 'error',
                            title: 'Form Errors',
                            html: errorMessages
                        });
                    } else {
                        Swal.fire(
                            'Error!',
                            data.message || 'An error occurred while updating the product.',
                            'error'
                        );
                    }
                }
            })
            .catch((error) => {
                Swal.fire(
                    'Error!',
                    'An error occurred while updating the product.',
                    'error'
                );
            });
        }
    });

    // Search Functionality with Autocomplete
    const searchInput = document.getElementById('searchInput');
    const productTableBody = document.getElementById('productTableBody');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            fetch(URLs.search_products + "?q=" + encodeURIComponent(query), {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Clear existing table body
                    productTableBody.innerHTML = '';
                    // Populate table with new data
                    data.products.forEach(product => {
                        // Create the table row manually
                        const row = document.createElement('tr');
                        row.id = `product-row-${product.id}`;
                        row.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-700');

                        // Checkbox Cell
                        const checkboxCell = document.createElement('td');
                        checkboxCell.classList.add('w-4', 'px-4', 'py-3', 'whitespace-nowrap');
                        checkboxCell.innerHTML = `
                            <div class="flex items-center">
                                <input id="checkbox-${product.id}" name="product_ids" value="${product.id}" type="checkbox" class="w-4 h-4 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                                <label for="checkbox-${product.id}" class="sr-only">Select product</label>
                            </div>
                        `;
                        row.appendChild(checkboxCell);

                        // Product Name Cell
                        const productCell = document.createElement('th');
                        productCell.scope = "row";
                        productCell.classList.add('flex', 'items-center', 'px-4', 'py-3', 'font-medium', 'text-gray-900', 'whitespace-nowrap', 'dark:text-gray-500');
                        productCell.innerHTML = `
                            ${product.photo_url ? `
                                <img 
                                    src="${product.photo_url}" 
                                    alt="${product.item_name}" 
                                    class="w-8 h-8 mr-3 object-cover rounded product-image cursor-pointer" 
                                    data-full-url="${product.photo_url}"
                                    title="Click to view full image"
                                >
                            ` : `
                                <img 
                                    src="${placeholderImageUrl}" 
                                    alt="${product.item_name}" 
                                    class="w-8 h-8 mr-3 object-cover rounded product-image cursor-pointer" 
                                    data-full-url="${placeholderImageUrl}"
                                    title="Click to view full image"
                                >
                            `}
                            ${product.item_name}  
                        `;
                        row.appendChild(productCell);

                        // Product Type Cell
                        const productTypeCell = document.createElement('td');
                        productTypeCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        productTypeCell.textContent = product.product_type_display;
                        row.appendChild(productTypeCell);

                        // Content Type Cell
                        const contentTypeCell = document.createElement('td');
                        contentTypeCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        contentTypeCell.textContent = product.content_type_display || 'N/A';
                        row.appendChild(contentTypeCell);

                        // Quantity Cell
                        const quantityCell = document.createElement('td');
                        quantityCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        quantityCell.textContent = product.quantity;
                        row.appendChild(quantityCell);

                        // UOM Cell
                        const uomCell = document.createElement('td');
                        uomCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        uomCell.textContent = product.uom;
                        row.appendChild(uomCell);

                        // Supplier Cell
                        const supplierCell = document.createElement('td');
                        supplierCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        supplierCell.textContent = product.supplier_name;
                        row.appendChild(supplierCell);

                        // Currency Code Cell
                        const currencyCell = document.createElement('td');
                        currencyCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        currencyCell.textContent = product.currency_code;
                        row.appendChild(currencyCell);

                        // Retail Price Cell
                        const priceCell = document.createElement('td');
                        priceCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        priceCell.textContent = `$${product.retail_price}`;
                        row.appendChild(priceCell);

                        // Discountable (All) Cell
                        const discountAllCell = document.createElement('td');
                        discountAllCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        discountAllCell.textContent = product.discountable_all ? 'Yes' : 'No';
                        row.appendChild(discountAllCell);

                        // Discountable (Members) Cell
                        const discountMembersCell = document.createElement('td');
                        discountMembersCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        discountMembersCell.textContent = product.discountable_members ? 'Yes' : 'No';
                        row.appendChild(discountMembersCell);

                        // Active Cell
                        const activeCell = document.createElement('td');
                        activeCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        activeCell.textContent = product.active ? 'Yes' : 'No';
                        row.appendChild(activeCell);

                        // Sellable Sets Cell
                        const sellableSetsCell = document.createElement('td');
                        sellableSetsCell.classList.add('px-4', 'py-3', 'whitespace-nowrap');
                        sellableSetsCell.textContent = product.product_type === 'Article' ? product.sellable_sets : 'N/A';
                        row.appendChild(sellableSetsCell);

                        // Actions Cell
                        const actionsCell = document.createElement('td');
                        actionsCell.classList.add('px-4', 'py-3', 'whitespace-nowrap', 'flex', 'space-x-2');
                        actionsCell.innerHTML = `
                            <!-- Edit Button -->
                            <button
                                type="button"
                                class="text-blue-600 hover:text-blue-800 focus:outline-none"
                                onclick="editProduct('${product.id}')"
                                title="Edit Product"
                                data-edit-url="${product.edit_url}"
                            >
                                <!-- Edit Icon -->
                                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828zM5 18a1 1 0 01-1-1v-4.586l10.293-10.293a1 1 0 011.414 0l2.586 2.586a1 1 0 010 1.414L9.414 17H5z" />
                                </svg>
                            </button>

                            <!-- Delete Button -->
                            <button
                                type="button"
                                class="text-red-600 hover:text-red-800 focus:outline-none"
                                onclick="deleteProduct('${product.id}')"
                                title="Delete Product"
                                data-delete-url="${product.delete_url}"
                            >
                                <!-- Delete Icon -->
                                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M6 3V4H4V6H16V4H14V3H6ZM6 6V15C6 16.1046 6.89543 17 8 17H12C13.1046 17 14 16.1046 14 15V6H6Z" />
                                </svg>
                            </button>
                        `;
                        row.appendChild(actionsCell);

                        // Append the row to the table body
                        productTableBody.appendChild(row);

                        // Re-attach event listener for the new image
                        const productImage = row.querySelector('.product-image');
                        if (productImage) {
                            productImage.addEventListener('click', function() {
                                const fullImageUrl = this.getAttribute('data-full-url');
                                const altText = this.getAttribute('alt');
                                Swal.fire({
                                    title: altText,
                                    imageUrl: fullImageUrl,
                                    imageAlt: altText,
                                    showCloseButton: true,
                                    showConfirmButton: false,
                                    width: 'auto',
                                    heightAuto: true,
                                    customClass: {
                                        popup: 'p-0 rounded-lg',
                                        image: 'object-contain w-auto h-96' // Adjust size as needed
                                    }
                                });
                            });
                        }
                    });

                    // Update "Select All" checkbox state
                    if (selectAllCheckbox) {
                        selectAllCheckbox.checked = false;
                    }

                } else {
                    Swal.fire(
                        'Error!',
                        data.message || 'An error occurred while searching.',
                        'error'
                    );
                }
            })
            .catch((error) => {
                Swal.fire(
                    'Error!',
                    'An error occurred while searching.',
                    'error'
                );
            });
        }, 300)); // Debounce delay of 300ms
    }

    // JavaScript to handle showing/hiding the linked_article and custom_content_type fields based on product_type and content_type
    const productTypeSelect = productForm.querySelector('select[name="product_type"]');
    const linkedArticleContainer = document.getElementById('linkedArticleContainer');
    const linkedArticleField = productForm.querySelector('select[name="linked_article"]');

    const contentTypeSelect = productForm.querySelector('select[name="content_type"]');
    const customContentTypeContainer = document.getElementById('customContentTypeContainer');
    const customContentTypeField = productForm.querySelector('input[name="custom_content_type"]');
    const uomSelect = productForm.querySelector('select[name="uom"]');

    // Function to show or hide the linked_article field based on product_type
    function toggleLinkedArticle() {
        const selectedType = productTypeSelect.value;
        if (selectedType === 'Component') {
            // Show and enable the linked_article dropdown
            linkedArticleContainer.classList.remove('hidden');
            linkedArticleField.disabled = false;
            // Populate linked_article dropdown
            populateLinkedArticles();
        } else {
            // Hide and disable the linked_article dropdown
            linkedArticleContainer.classList.add('hidden');
            linkedArticleField.disabled = true;
            linkedArticleField.innerHTML = '<option value="">Select Article</option>'; // Clear options
        }
        calculateSellableSets();
    }

    // Function to show or hide the custom_content_type input based on content_type
    function toggleCustomContentType() {
        const selectedContentType = contentTypeSelect.value;
        if (selectedContentType === 'Other') {
            customContentTypeContainer.classList.remove('hidden');
            customContentTypeField.disabled = false;
            // Disable UOM if 'Other' should allow free-form UOM
            updateUomOptions('Other');
            uomSelect.disabled = true;
            uomSelect.value = ''; // Clear UOM if it's disabled
        } else {
            customContentTypeContainer.classList.add('hidden');
            customContentTypeField.disabled = true;
            customContentTypeField.value = ''; // Clear custom content type input
            // Update UOM options based on the selected content_type
            const selectedContentType = contentTypeSelect.value;
            updateUomOptions(selectedContentType);
            uomSelect.disabled = false;
        }
        calculateSellableSets();
    }

    // Function to calculate and update Sellable Sets
    function calculateSellableSets() {
        const selectedType = productTypeSelect.value;
        if (selectedType === 'Article') {
            const retailPrice = parseFloat(productForm.querySelector('input[name="retail_price"]').value) || 0;
            const linkedArticleId = productForm.querySelector('select[name="linked_article"]').value;
            let componentPrice = 0;

            if (linkedArticleId) {
                // Fetch the linked component's price via AJAX
                let editUrl = URLs.edit_product.replace('/0/', `/${linkedArticleId}/`);
                fetch(editUrl, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        componentPrice = parseFloat(data.product.retail_price) || 0;
                        const sellableSets = componentPrice > 0 ? Math.floor(retailPrice / componentPrice) : 'N/A';
                        // Update Sellable Sets in the modal if needed
                        // For example, you can add a readonly input field to show sellable sets
                        // Assuming there's an element with id 'sellableSetsDisplay' to show this value
                        let sellableSetsDisplay = document.getElementById('sellableSetsDisplay');
                        if (sellableSetsDisplay) {
                            sellableSetsDisplay.textContent = sellableSets;
                        }
                    }
                })
                .catch((error) => {
                    console.log('Error fetching component price:', error);
                });
            }
        }
    }

    // Initial setup based on current selections
    if (productTypeSelect && contentTypeSelect) {
        toggleLinkedArticle();
        toggleCustomContentType();
    }

    // Initialize UOM options based on current content_type
    if (contentTypeSelect && uomSelect) {
        updateUomOptions(contentTypeSelect.value, uomSelect.value);
    }

    // Add event listeners for changes in product_type and content_type
    if (productTypeSelect) {
        productTypeSelect.addEventListener('change', toggleLinkedArticle);
    }
    if (contentTypeSelect) {
        contentTypeSelect.addEventListener('change', toggleCustomContentType);
    }

    // Add event listener to retail_price and linked_article fields to recalculate Sellable Sets
    const retailPriceInput = productForm.querySelector('input[name="retail_price"]');
    const linkedArticleSelect = productForm.querySelector('select[name="linked_article"]');

    if (retailPriceInput) {
        retailPriceInput.addEventListener('input', calculateSellableSets);
    }
    if (linkedArticleSelect) {
        linkedArticleSelect.addEventListener('change', calculateSellableSets);
    }

    // Feature 2: Automatically calculate and populate quantity field in the modal
    function updateQuantityField() {
        const linkedArticleId = linkedArticleSelect.value;
        const retailPrice = parseFloat(retailPriceInput.value);
        if (linkedArticleId && !isNaN(retailPrice)) {
            fetch(URLs.get_sellable_sets + "?article_id=" + encodeURIComponent(linkedArticleId), {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    quantityInput.value = data.sellable_sets;
                } else {
                    quantityInput.value = '';
                }
            })
            .catch(error => {
                console.log('Error fetching sellable sets:', error);
                quantityInput.value = '';
            });
        } else {
            quantityInput.value = '';
        }
    }

    const quantityInput = productForm.querySelector('input[name="quantity"]');
    if (linkedArticleSelect && retailPriceInput && quantityInput) {
        linkedArticleSelect.addEventListener('change', updateQuantityField);
        retailPriceInput.addEventListener('input', updateQuantityField);
    }

    // Re-attach event listeners for product images after dynamic content
    function attachImageClickEvents() {
        document.querySelectorAll('.product-image').forEach(function(image) {
            image.addEventListener('click', function() {
                const fullImageUrl = this.getAttribute('data-full-url');
                const altText = this.getAttribute('alt');
                Swal.fire({
                    title: altText,
                    imageUrl: fullImageUrl,
                    imageAlt: altText,
                    showCloseButton: true,
                    showConfirmButton: false,
                    width: 'auto',
                    heightAuto: true,
                    customClass: {
                        popup: 'p-0 rounded-lg',
                        image: 'object-contain w-auto h-96' // Adjust size as needed
                    }
                });
            });
        });
    }

    attachImageClickEvents();
});
