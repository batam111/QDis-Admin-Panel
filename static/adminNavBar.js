function selectNav(selectedOption=1){
    var element1 = document.getElementById("users");
    var element2 = document.getElementById("userPosts");
    var element3 = document.getElementById("hashTags");
    switch(selectedOption){
        case 1:
            element2.classList.remove("active");
            element3.classList.remove("active");
            element1.classList.add("active");     
            break;
        case 2:
            element1.classList.remove("active");
            element3.classList.remove("active");
            element2.classList.add("active");
            break;
        case 3:
            element2.classList.remove("active");
            element1.classList.remove("active");
            element3.classList.add("active");
            break;
        default:

    }
}