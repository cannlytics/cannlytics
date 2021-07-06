/**
 * User Interface JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 5/2/2021
 * Updated: 7/4/2021
 */
import { deserializeForm, getCookie, hasClass } from '../utils.js';


const formHelpers = {


  submitForm(inputId, url) {
    /*
     * FIXME: Submit a form without refreshing the page.
     */
    var selectedFile = $(`#${inputId}`).files[0];
    var fd = new FormData();
    fd.append('file', selectedFile);
    $.ajax({
      method: 'POST', 
      url: url,
      data: fd, 
      headers: {
        'Content-Type': undefined, 
        'X-CSRFToken': getCookie('csrftoken')
      },
      cache: false, 
      processData: false
    })
    .done(function(data) {
      alert(data)
    });
  },


  submitFormWithoutRefresh(formId, url) {
    /*
     * FIXME: Submit a form without refreshing the page.
     */
    $(`#${formId}`).on('submit', function(e) {
      e.preventDefault();
      $.ajax({
          type:'POST',
          url: url,
          data: { csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val() },
        });
      });
  },


  toggleFields(event, key) {
    /*
     * Hide or show additional form fields.
     */
    event.preventDefault();
    this.toggleElementClass(`${key}-fields`, 'd-none');
    this.toggleElementClass(`${key}-fields-show`, 'd-none');
    try {
      this.toggleElementClass(`${key}-fields-hide`, 'd-none');
    } catch (error) {
      // No element to hide the form.
    }
  },


};


const initHelpers = {


  enableTooltips() {
    /*
     * FIXME: Enable all tooltips on a page.
     * Uncaught ReferenceError: bootstrap is not defined
     */
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    return tooltipList;
  },


};


export const navigationHelpers = {


  openObject(model, modelSingular, data) {
    /*
     * Navigate a selected object detail page, saving its data in local storage.
     * It is assumed that data has a field named as the singular modal name +
     * an underscore + the literal 'id'. If no ID is provided, then navigate to
     * a new page.
     */
    let id = 'new';
    const objectId = data[`${modelSingular}_id`];
    if (objectId) id = objectId;
    localStorage.setItem(modelSingular, JSON.stringify(data));
    window.location.href = `/${model}/${id}`;
  },


  viewObject(modelSingular) {
    /*
     * View an object's data from local storage when navigating to a detail page.
     */
    const data = JSON.parse(localStorage.getItem(modelSingular));
    deserializeForm(document.forms[`${modelSingular}-form`], data)
    console.log('DEV: Observation data:', data);
  },


};


export const ui = {

  ...formHelpers,
  ...initHelpers,
  ...navigationHelpers,

  choosePhoto(id) {
    /*
     * Choose a file to upload.
     */
    document.getElementById(id).click();
  },


  hideSidebar() {
    /*
     * Hides the console sidebar.
     */
    const sidebar = document.getElementById('sidebar-menu');
    // const sidebarToggle = document.getElementById('sidebar-console-toggle');
    const navbarToggle = document.getElementById('navbar-menu-button');
    sidebar.classList.add('d-none');
    sidebar.classList.remove('d-md-block');
    // sidebarToggle.classList.remove('d-md-none');
    navbarToggle.classList.remove('d-md-none');
  },


  showSidebar() {
    /*
     * Show the console sidebar.
     */
    const sidebar = document.getElementById('sidebar-menu');
    const sidebarToggle = document.getElementById('sidebar-console-toggle');
    sidebar.classList.remove('d-none');
    sidebar.classList.add('d-md-block');
    sidebarToggle.classList.add('d-md-none');
  },


  toggleSidebarNestedNav(section) {
    /*
     * Toggle nested navigation in the sidebar.
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

  addListItem(event, type) {
    /*
     * Adds a list item of input fields to the UI by
     * cloning the primary list item and clearing its fields.
     * The delete button is shown and wired-up.
     * The tooltip is removed.
     */
    // FIXME: Generalize to handle adding data model fields? Or create a new function.
    event.preventDefault();
    var ul = document.getElementById(`${type}-list`);
    var li = document.getElementById(`primary-${type}`).cloneNode(true);
    var id = `${type}-${ul.children.length + 1}`;
    li.setAttribute('id', id);
    ul.appendChild(li);
    $(`#${id} input`).val('');
    $(`#${id} .btn-tooltip-help`).remove();
    var deleteButton = $(`#${id} .btn-link`);
    deleteButton.removeClass('d-none');
    deleteButton.attr('onClick', `cannlytics.ui.removeListItem(event, '${type}-list', '${id}');`);
  },


  removeListItem(event, listId, elementId) {
    /*
     * Remove an element from a list.
     */
    event.preventDefault();
    var ul = document.getElementById(listId);
    var item = document.getElementById(elementId);
    ul.removeChild(item);
  },


  toggleElementClass(id, className) {
    /*
     * Show or hide a given element.
     */
    const element = document.getElementById(id);
    element.classList.toggle(className);
  },


  showLoadingButton(buttonId) {
    /*
     * Show a hidden loading button given the ID of its button counterpart.
     */
    document.getElementById(buttonId).classList.add('d-none');
    document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
  },


  hideLoadingButton(buttonId) {
    /*
     * Hide a by-default hidden loading button given the ID of its button counterpart.
     */
    document.getElementById(buttonId).classList.add('d-none');
    document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
  },


};
