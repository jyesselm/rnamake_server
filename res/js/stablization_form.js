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
  /*var fields = ['pdb_file_name', 'start_bp', 'end_bp', 'nstruct']
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

  // check to make sure that start_bp and end_bp are correctly formatted
  fields = ['start_bp', 'end_bp']
  fields.forEach(function(field) {
    var fn = document.getElementById(field).value;
    var spl = fn.split("-");
    if(spl.length != 2) {
      alert(
        field + " must be composed of two residue names seperated by a '-'. " +
        "Example: A221-A252, which is residue 221 on chain A base paired to residue " +
        "252 also on chain A. For more info see detailed instructions");
        return false;
    }
    console.log(spl);
  });*/
  return true;


  //if(fail) { return false; }
  //else     { return true;  }
}
