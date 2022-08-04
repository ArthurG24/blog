var elements = ["nav",
"article", 
"aside", 
"edit-article", 
"aside-h2", 
"article-header", 
"aside-header", 
"h3",
"foot-link",
"keywords-input",
"submit-button",
"admin-buttons",
"categories-input",
"title-input",
"file-label",
"input-date",
"label-date",
"delete-button",
"status-input",
"thumb"];

const checkbox = document.getElementById('checkbox');

window.addEventListener("load", ()=>{

  if (localStorage.getItem("theme") == "light") {
    
    tinymce.init({
      selector: 'textarea',
      content_style:
        "body { background: #e1e1e1; color: #03121a; font-size: 1.2em; font-family: Verdana, Arial, Tahoma, Serif; }",
      // plugins: 'a11ychecker advcode casechange export formatpainter image editimage linkchecker autolink lists link checklist media mediaembed pageembed permanentpen powerpaste table advtable tableofcontents tinycomments tinymcespellchecker',
      // toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      plugins: 'table',
      toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      toolbar_mode: 'floating',
      tinycomments_mode: 'embedded',
      tinycomments_author: 'Author name',
      skin_url: "/static/styles/skins/ui/light",
      content_css: "/static/styles/skins/content/light/content.min.css",
      });

    document.body.classList.add("light");
    checkbox.checked = true;

    for(var i = 0; i < elements.length; i++) {
      elem = document.getElementsByClassName(elements[i]);
      for(var j = 0; j < elem.length; j++) {
      elem[j].classList.add("light");
      }
    }
  }
  
  else {
    tinymce.init({
      selector: 'textarea',
      content_style:
        "body { background: #03141d; color: #cfcbc5; font-size: 1.2em; font-family: Verdana, Arial, Tahoma, Serif; }",
      // plugins: 'a11ychecker advcode casechange export formatpainter image editimage linkchecker autolink lists link checklist media mediaembed pageembed permanentpen powerpaste table advtable tableofcontents tinycomments tinymcespellchecker',
      // toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      plugins: 'table',
      toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      toolbar_mode: 'floating',
      tinycomments_mode: 'embedded',
      tinycomments_author: 'Author name',
      skin_url: "/static/styles/skins/ui/custom-dark",
      content_css: "/static/styles/skins/content/custom-dark/content.min.css",
      });
  }
})


checkbox.addEventListener("change", ()=>{

  if (event.currentTarget.checked) {
    
    tinymce.remove();

    tinymce.init({
      selector: 'textarea',
      content_style:
        "body { background: #e1e1e1; color: #cfcbc5; font-size: 1.2em; font-family: Verdana, Arial, Tahoma, Serif; }",
      // plugins: 'a11ychecker advcode casechange export formatpainter image editimage linkchecker autolink lists link checklist media mediaembed pageembed permanentpen powerpaste table advtable tableofcontents tinycomments tinymcespellchecker',
      // toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      plugins: 'table',
      toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      toolbar_mode: 'floating',
      tinycomments_mode: 'embedded',
      tinycomments_author: 'Author name',
      skin_url: "/static/styles/skins/ui/light",
      content_css: "/static/styles/skins/content/light/content.min.css",
      });

    document.body.classList.add("light");

    for(var i = 0; i < elements.length; i++) {
      elem = document.getElementsByClassName(elements[i]);
      for(var j = 0; j < elem.length; j++) {
        elem[j].classList.add("light");
      }
    }

    localStorage.setItem("theme", "light");
  }

  else {
    tinymce.remove();

    tinymce.init({
      selector: 'textarea',
      content_style:
        "body { background: #03141d; color: #03121a; font-size: 1.2em; font-family: Verdana, Arial, Tahoma, Serif; }",
      // plugins: 'a11ychecker advcode casechange export formatpainter image editimage linkchecker autolink lists link checklist media mediaembed pageembed permanentpen powerpaste table advtable tableofcontents tinycomments tinymcespellchecker',
      // toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      plugins: 'table',
      toolbar: 'casechange checklist code export table tableofcontents h2 h3 underline italic bold link',
      toolbar_mode: 'floating',
      tinycomments_mode: 'embedded',
      tinycomments_author: 'Author name',
      skin_url: "/static/styles/skins/ui/custom-dark",
      content_css: "/static/styles/skins/content/custom-dark/content.min.css",
      });

    document.body.classList.remove("light");

    for(var i = 0; i < elements.length; i++) {
      elem = document.getElementsByClassName(elements[i])

      for(var j = 0; j < elem.length; j++) {
        elem[j].classList.remove("light");
      }
    }

    localStorage.setItem("theme", "dark");
  }

}) 

  
    
    
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


