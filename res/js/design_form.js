// to display name of file in text box
$(document).on('change', '.btn-file :file', function() {
  var input = $(this),
    numFiles = input.get(0).files ? input.get(0).files.length : 1,
    label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  input.trigger('fileselect', [numFiles, label]);
});

$(document).ready(function() {
  $('.btn-file :file').on('fileselect', function(event, numFiles, label) {
    var input = $(this).parents('.input-group').find(':text'),
      log = numFiles > 1 ? numFiles + ' files selected' : label;
    if (input.length) {
      // not sure how else to trigger this
      document.getElementById('pdb_file_name').style.borderColor = "";
      input.val(log);
    } else {
      if (log) alert(log);
    }

  });
});

//form validation
function FormValidation() {
  var fields = ['pdb_file_name', 'start_bp', 'end_bp', 'nstructs']
  fields.forEach(function(field) {
    var fn = document.getElementById(field).value;
    if(fn == "") {
      document.getElementById(field).style.borderColor = "red";
      fail = true;
    }
    else {
      document.getElementById(field).style.borderColor = "";

    }
  });

  if(fail) { return false; }
  else     { return true;  }
}
