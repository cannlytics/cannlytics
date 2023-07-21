/**
 * User Interface JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 5/2/2021
 * Updated: 12/16/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { Modal, Tooltip } from 'bootstrap';
import { deserializeForm, serializeForm, getCookie, hasClass } from '../utils.js';

export function showLoadingButton(buttonId) {
  /**
   * Show a hidden loading button given the ID of its button counterpart.
   * @param {String} buttonId The element ID of the loading button.
   */
  document.getElementById(buttonId).classList.add('d-none');
  document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
};

export function hideLoadingButton(buttonId) {
  /**
   * Hide a by-default hidden loading button given the ID of its button counterpart.
   * @param {String} buttonId The element ID of the loading button.
   */
  document.getElementById(buttonId).classList.add('d-none');
  document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
};

export function showModal(id) {
  /**
   * Show a modal given its ID.
   * @param {String} buttonId The element ID of the loading button.
   */
  const observationModal = Modal(document.getElementById(id));
  observationModal.show();
};

export function hideModal(id) {
  /**
   * Hide a modal given its ID.
   * @param {String} id The element ID of the loading button.
   */
  const observationModal = Modal(document.getElementById(id));
  observationModal.hide();
};

const formHelpers = {

  addListItem(event, type) {
    /**
     * Adds a list item of input fields to the UI by
     * cloning the primary list item and clearing its fields.
     * The delete button is shown and wired-up.
     * The tooltip is removed.
     * @param {Event} event A user-driven event.
     * @param {String} type The type of item being rendered in the list.
     */
    // TODO: Generalize to handle adding data model fields? Or create a new function.
    event.preventDefault();
    const ul = document.getElementById(`${type}-list`);
    const li = document.getElementById(`primary-${type}`).cloneNode(true);
    const id = `${type}-${ul.children.length + 1}`;
    li.setAttribute('id', id);
    ul.appendChild(li);
    // TODO: WEEN OFF OF JQUERY!!!
    $(`#${id} input`).val('');
    $(`#${id} .btn-tooltip-help`).remove();
    const deleteButton = $(`#${id} .btn-link`);
    deleteButton.removeClass('d-none');
    deleteButton.attr('onClick', `cannlytics.ui.removeListItem(event, '${type}-list', '${id}');`);
  },

  removeListItem(event, listId, elementId) {
    /**
     * Remove an element from a list.
     * @param {Event} event A user-driven event.
     * @param {String} listId The element ID of the list being rendered.
     * @param {String} elementId The element ID of the list item being removed.
     */
    event.preventDefault();
    const ul = document.getElementById(listId);
    const item = document.getElementById(elementId);
    ul.removeChild(item);
  },

  chooseFile(id) {
    /**
     * Choose a file to upload.
     */
    document.getElementById(id).click();
  },

  toggleElementClass(id, className) {
    /**
     * Show or hide a given element.
     * @param {String} id The element ID of an element to toggle it's class.
     * @param {String} className The class name to add or remove from the element.
     */
    const element = document.getElementById(id);
    element.classList.toggle(className);
  },

  toggleFields(event, key) {
    /**
     * Hide or show additional form fields.
     * @param {Event} event A user-driven event.
     * @param {String} key A specific field key.
     */
    event.preventDefault();
    this.toggleElementClass(`${key}-fields`, 'd-none');
    this.toggleElementClass(`${key}-fields-show`, 'd-none');
    try {
      this.toggleElementClass(`${key}-fields-hide`, 'd-none');
    } catch (error) { /* No fields to hide. */ }
  },

  renderForm(id, fields) {
    /**
     * Render a form given an Id and fields.
     * @param {String} id The element ID of the form.
     * @param {Array} fields A list of fields to render.
     */
    const form = document.getElementById(id);
    form.innerHTML = '';
    fields.forEach((field) => {
      if (!field.type || field.type == 'text') form.innerHTML += this.renderFormTextInput(field);
      else if (field.type =='textarea') form.innerHTML += this.renderFormTextArea(field);
      else if (field.type =='checkbox') form.innerHTML += this.renderFormCheckbox(field);
    });
  },

  renderFormTextInput(options) {
    /**
     * Render a form text input given it's options.
     * @param {Object} options A set of options, including: `label`, `key`,
     * `disabled`, `readonly`, `type`, `class`, and `style`.
     * @returns {String} Returns the rendered HTML.
     */
    let html = `<div class="row mb-3">
      <label class="col-sm-3 col-form-label col-form-label-sm">
        ${options.label}
      </label>
      <div class="col-sm-9">
        <input
          type="text"
          id="input_${options.key}"
          class="form-control form-control-sm ${options.class}"
          name="${options.key}"
          spellcheck="false"
          style="${options.style}"
          type="${options.type}"`;
    if (options.disabled) html += `\ndisabled`;
    if (options.readonly) html += `\readonly`;
    html += `>
      </div>
    </div>`;
    return html;
  },

  renderFormDateInput(options) {
    /** Render a form date input given it's options. */
    // TODO: Implement.
  },

  renderFormDateTimeInput(options) {
    /** Render form date and time inputs given it's options. */
    // TODO: Implement.
  },

  renderFormTextArea(options) {
    /**
     * Render a form text area given it's options.
     * @param {Object} options A set of options, including: `label`, `key`,
     * `disabled`, `readonly`, `type`, `class`, and `style`.
     * @returns {String} Returns the rendered HTML.
     */
    let html = `
    <div class="form-floating mb-3">
      <textarea
        id="input_${options.key}"
        name="${options.key}"
        class="form-control"
        placeholder=""
        style="height:250px"
      `;
      if (options.disabled) html += `\ndisabled`;
      if (options.readonly) html += `\readonly`;
      html += `
      ></textarea>
      <label for="input_${options.key}">
        ${options.label}
      </label>
    </div>`;
    return html;
  },

  renderFormCheckbox(options) {
    /** Render a form checkbox given it's options. */
    // TODO: Implement.
  },

  renderFormSelect(options) {
    /** Render a form select given it's options. */
    // TODO: Implement.
  },

  // Optional: Render other field types:
  // - Images
  // - Numbers / integers
  // - Lists

};

export const initHelpers = {

  initializeTooltips() {
    /**
     * Initialize Bootstrap toasts.
     */
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    return tooltipTriggerList.map((tooltipTriggerEl) => new Tooltip(tooltipTriggerEl) );
  },

};

export const navigationHelpers = {

  getFormData(formId) {
    /**
     * Get the data from a form from a template.
     * @param {String} formId The element ID of the form to render the data.
     */
    return serializeForm(document.forms[formId]);
  },

  navigateUp(url) {
    /** 
     * Remove the last directory in URL, navigating up.
     * @param {String} url The downstream URL of the parent URL to locate.
     */
    window.location.href = window.location.href.substring(0, url.lastIndexOf('/'));
  },

  openObject(model, modelSingular, data) {
    /**
     * Navigate a selected object detail page, saving its data in local storage.
     * It is assumed that data has a field named as the singular modal name +
     * an underscore + the literal 'id'. If no ID is provided, then navigate to
     * a new page.
     * @param {String} model The type of data model.
     * @param {String} modelSingular The singular type of data model.
     * @param {Object} data The data to open in a detail page.
     */
    let id = 'new';
    const objectId = data[`${modelSingular}_id`];
    if (objectId) id = objectId;
    localStorage.setItem(modelSingular, JSON.stringify(data));
    window.location.href = `${window.location.href}/${id}`;
  },

  toggleSidebar(id, breakpoint = 768) {
    /**
     * Toggle the sidebar depending on the screen size,
     * showing the sidebar on large screens and hiding the sidebar
     * on small screens on initialization and when the screen size changes.
     * @param {String} id The element ID of the sidebar.
     * @param {Number} breakpoint The pixels at which a small screen turns
     *    into a large screen.
     */
    let maximized = 0;
    if ($(window).width() < breakpoint) {
      document.getElementById(id).classList.remove('show');
    }
    else {
      maximized = 1;
    }
    $(window).on('resize', function() {
      if ($(window).width() < breakpoint) {
        if (maximized) {
          document.getElementById(id).classList.remove('show');
          maximized = 0;
        }
      } else {
        if (!maximized) {
          document.getElementById(id).classList.add('show');
          maximized = 1;
        }
      }
    });
  },

  toggleSidebarNestedNav(section) {
    /**
     * Toggle nested navigation in the sidebar.
     * @param {String} section The nested section to reveal or hide.
     */
    const items = document.getElementById(`${section}-items`);
    const toggle = document.getElementById(`${section}-toggle`);
    if (hasClass(items, 'show')) {
      items.classList.remove('show');
      toggle.classList.remove('flipped');
    } else {
      items.classList.add('show');
      toggle.classList.add('flipped');
    }
  },

  viewObject(modelSingular) {
    /**
     * View an object's data from local storage when navigating to a detail page.
     * @param {String} modelSingular The singular type of data model.
     */
    const data = JSON.parse(localStorage.getItem(modelSingular));
    deserializeForm(document.forms[`${modelSingular}-form`], data)
  },

  hideElement(id) {
    /**
     * Hide a specific element in the user interface, by applying a `d-none` class.
     */
    document.getElementById(id).classList.add('d-none');
  },

  showElement(id) {
    /**
     * Show a specific element in the user interface, by removing a `d-none` class.
     */
    document.getElementById(id).classList.remove('d-none');
  },
  
};

export const ui = {
  ...formHelpers,
  ...initHelpers,
  ...navigationHelpers,
  hideLoadingButton,
  showLoadingButton,
  hideModal,
  showModal,
};
