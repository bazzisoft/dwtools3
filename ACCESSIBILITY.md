HTML5 Accessibility Requirements & Guidelines
=============================================

Website
-------
- Must provide a HTML sitemap with a linke somewhere not just an XML one for search engines.

- Main landmarks (eg. `<header>`, `<footer>`, `<main>`, `<nav>`) and other main navigational elements should have `aria-label` or `aria-labelledby` defined to indicate what they represent.

- Use `aria-live` regions for dynamically updated content. Set a `<div>` or other element to `role="region|status|log|alert|progressbar"` and set `aria-live="polite|assertive"` (prefer polite!). Ensure this `div` always remains in the DOM. The screen reader should then read updates when the content inside changes.
 

Images
------
- Use webfonts or SVGs wherever possible for icons and other non-photo images.

- Avoid images where possible (excepting photos), they are a often source of contrast issues.

- Avoid placing text over images/photos.

- Avoid animated/flickering images as they may affect epilepsy & ADD users.


Keyboard Navigation
-------------------
- All clickable elements should be available via TAB key.

- All links should have a "href" attribute (even if "#") so they are available for keyboard navigation.

- The first link on the page should be a hidden "skip to main content", which jumps down to an anchor where the real page content begins. Best way to implement this is to position the link absolutely off screen until focussed, and then place it on screen somewhere at the top left.

- The focus indicator must be clearly visible on all clickable elements. If it's not clear enough, it can be strengthed or replaced, eg:

        .strong-focus {
            &:focus {
                outline: none;
                box-shadow: 0 0 5px #ffff00;
            }
        }



Buttons & Links
---------------
- Ensure all buttons and links have a readable description (vs just an icon). This can be done with tooltips (`title="xxx"`), an `aria-label` attribute or `<span class="sr-only"/>` text in the link/button body.

- Ensure all links and buttons have a context-specific tooltip, eg _"Read more about xxx"_ vs _"Read more"_.

- Links which behave as buttons should have `role="button"`.

- Links should not be "doubled" else they will be read twice. If you have an image link then a text link pointing to the same place, set `tabindex="-1"` on the image link to skip it. 

- Toggle buttons should have `role="button"` and `aria-pressed="true|false"` as appropriate.

- Simulated checkboxes should have `role="checkbox"` and  `aria-pressed="true|false|mixed"` as appropriate.

- Group related links inside a `<nav>` element with an `aria-label` to indicate its purpose.


Tabs & Dropdowns
----------------

- Avoid aria roles for tabs, pills and dropdowns as most screen reader & browser combinations don't work well with them.  

- The selected tab or dropdown trigger should have `aria-expanded="true"`. Unselected tabs or closed dropdown triggers should have `aria-expanded="false"`. 

- A dropdown trigger should have `aria-haspopup="true"`.

- The opened dropdown menu or tab panel should have `aria-labelledby` defined and pointing to the trigger element. 

- After triggering a tab or dropdown the opened panel or menu should receive the focus or at least the next TAB stop.


Forms
-----
- Ensure all forms have `aria-label` or `aria-labelledby` defined so the screen reader can read it out when the form is focussed.

- All form input elements should be wrapped in a `<label>`, have a `<label for="xxx">` pointing at them, or provide a `title` tooltip or `aria-label` describing them.

- The success message for an Ajax-submitted form will need `role="alert"` so it is read out. Might need to be added with a delay.

- If a form fails validation we need that fact to be read out and the validation errors on each field readable by a screen reader:

    - Add an (optionally hidden) alert to indicate the form has failed validation: `<div class="sr-only" role="alert">Form contains errors, please review and try again.</div>`. May require a delay.

    - Focus the first form field containing the error, or at minimum the first form field. May require a delay.
    
    - Each invalid form field input should contain `aria-invalid="true"` as well as `aria-describedby` pointing to the element containing the error message.     

- If you have a group of radio buttons or checkboxes with a common label, wrap them and the label in a `<fieldset>` element and use either a `<legend>` element around the label or `aria-label` / `aria-labelledby` on the `<fieldset>` pointing to the label. 


Global Alerts/Success/Error Messages
------------------------------------
- Ensure all alert messages have `role="alert"` so they are automatically read by the screen reader, both if rendered on page or triggered via Ajax.


Dialogs/Modals/Popups
---------------------
- When the dialog is opened, focus must be set to the first focusable item inside it.

- Use `role="dialog"` in the outer div, `role="document"` in the inner div.

- Use `aria-label` or `aria-labelledby` to indicate the title of the dialog, and `aria-description` or `aria-describedby` to indicate the content that should be read when the dialog is opened. Prefer the `aria-___by` versions where possible.

- Eg.

        <div class="modal fade" tabindex="-1" role="dialog" aria-labelledby="modal-title" aria-describedby="modal-desc">
          <div class="modal-dialog" role="document">
            <div class="modal-content">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <div class="modal-body">
                <h4 id="modal-title">Modal title</h4>
                <p id="modal-desc">One fine body&hellip;</p>
              </div>
            </div><!-- /.modal-content -->
          </div><!-- /.modal-dialog -->
        </div><!-- /.modal -->

