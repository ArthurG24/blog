tinymce.init({
    selector: 'textarea',
    // plugins: 'a11ychecker advcode casechange export formatpainter image editimage linkchecker autolink lists link checklist media mediaembed pageembed permanentpen powerpaste table advtable tableofcontents tinycomments tinymcespellchecker',
    // toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
    plugins: 'table',
    toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
    toolbar_mode: 'floating',
    tinycomments_mode: 'embedded',
    tinycomments_author: 'Author name',
    skin_url: "/static/styles/skins/ui/custom-dark",
    content_css: "/static/styles/skins/content/custom-dark/content.css",
    });
  
  
    
    
const chooseFile = document.getElementById("thumb");
const imgPreview = document.getElementById("img-preview");
    
chooseFile.addEventListener("change", function () {
  getImgData();
});
    
function getImgData() {
  const files = chooseFile.files[0];
  if (files) {
    const fileReader = new FileReader();
    fileReader.readAsDataURL(files);
    fileReader.addEventListener("load", function () {
      imgPreview.style.display = "block";
      imgPreview.innerHTML = '<img src="' + this.result + '" />';
      document.getElementById("img-preview-edit").style.display = "None"
    });    
  }
}
    

dt = new Date()
dt.setSeconds(0, 0)
dt.setHours(dt.getHours() + 2)
console.log(dt);
document.getElementById('calendar').valueAsDate = dt;


