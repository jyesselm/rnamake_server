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
  // check to make sure all form items are filled
  var fields = ['pdb_file_name', 'nstruct']
  var fail = false;
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

  // check to make sure nstruct is a number
  var nstruct = parseInt(document.getElementById('nstruct').value);
  if(isNaN(nstruct)) {
    alert("# designs must be a number from 1 to 100");
    return false;
  }
  if(nstruct > 100 || nstruct < 1) {
    alert("# designs must be a number from 1 to 100");
    return false;
  }
  
  if(fail) { return false; }
  else     { return true;  }
}
