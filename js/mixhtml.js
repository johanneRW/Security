function cl(text){console.log(text)}

try{
    history.replaceState({"mixonurl":mix_replace_url}, "title", mix_replace_url)
}catch(err){
    
}


// ##############################
async function mixhtml(el=false){
    
    if( !el ){
        el = event.target
    }


    let url = ""
    if( el.hasAttribute("mix-get") ){ url = el.getAttribute("mix-get") }
    if( el.hasAttribute("mix-post") ){ url = el.getAttribute("mix-post") }
    if( el.hasAttribute("mix-put") ){ url = el.getAttribute("mix-put") }
    if( el.hasAttribute("mix-delete") ){ url = el.getAttribute("mix-delete") }
    if(url == ""){ cl(`mix-method missing, therefore url not found`); return }
    cl(`url: ${url}`)

    if( document.querySelector(`[mix-on-url="${url}"]`) ){
        cl("SPA already loaded, showing elements")
        mixonurl(url)
        return
    }

    mix_fetch_data(el)

}

// ##############################
async function mix_fetch_data(el){
    // cl(`mix_fetch_data()`)

    let method = ""
    if( el.hasAttribute("mix-get") ){ method = "get" }
    if( el.hasAttribute("mix-post") ){ method = "post" }
    if( el.hasAttribute("mix-put") ){ method = "put" }
    if( el.hasAttribute("mix-delete") ){ method = "delete" }

    // cl(`ok : mix_fetch_data() method to fetch data is ${el.getAttribute("mix-method")}`)   
    let url = el.getAttribute("mix-"+method).includes("?") ? `${el.getAttribute("mix-"+method)}&spa=yes` : `${el.getAttribute("mix-"+method)}?spa=yes` 
    
    // cl("url: " + url)

    if(method == "post" || method == "put"){
        if( ! el.getAttribute("mix-data") ){cl(`error : mix_fetch_data() mix-data missing`); return}
        if( ! document.querySelector(el.getAttribute("mix-data")) ){cl(`error - mix-data element doesn't exist`); return} 
        const frm = document.querySelector(el.getAttribute("mix-data"))
        // Validation inside each element of the form
        let errors = false
        const attrs = frm.querySelectorAll("[mix-check]")
        for(let i = 0; i < attrs.length; i++){
            attrs[i].classList.remove("mix-error") 
            // const regex = "^"+attrs[i].getAttribute("mix-check")+"$"
            const regex = attrs[i].getAttribute("mix-check")
            re = new RegExp(regex)
            cl(re.test(attrs[i].value))
            if( ! re.test(attrs[i].value) ){
                cl("mix-check failed")
                attrs[i].classList.add("mix-error") 
                errors = true
            }
        }  
        if(errors) return
    }   
    
    if(el.getAttribute("mix-await")){
        el.disabled = true
        el.innerHTML = el.getAttribute("mix-await")
    }    

    if(el.getAttribute("mix-wait")){
        el.classList.add("mix-hidden")
        document.querySelector(el.getAttribute("mix-wait")).classList.remove("mix-hidden")
    }
    let conn = null
    if(["post", "put", "patch", "delete"].includes(method)) {
        let formData;
        
        if(method === "delete") {
            // For DELETE requests, get the form that contains the delete button
            const form = el.closest('form')
            formData = new FormData(form)
            // If no form found, create new FormData
            if (!form) {
                formData = new FormData()
            }
        } else {
            // For other methods, get data from the form
            const form = document.querySelector(el.getAttribute("mix-data"))
            formData = new FormData(form)
        }
        
        // Add CSRF token if not present
        if (!formData.has('csrf_token')) {
            const token = document.cookie.split('; ')
                .find(row => row.startsWith('csrf_token='))
                ?.split('=')[1]
            if (token) formData.append('csrf_token', token)
        }
        
        conn = await fetch(url, {
            method: method,
            body: formData
        })        
    } else {   
        conn = await fetch(url, {
            method : method
        })
    }

    if(el.getAttribute("mix-await")){
        el.disabled = false
        el.innerHTML = el.getAttribute("mix-default")
    }    

    if(el.getAttribute("mix-wait")){
        el.classList.remove("mix-hidden")
        document.querySelector(el.getAttribute("mix-wait")).classList.add("mix-hidden")
    }    

    res = await conn.text()
    
    // Add sanitization before inserting
    const sanitizedHtml = sanitizeHtml(res)
    document.querySelector("body").insertAdjacentHTML('beforeend', sanitizedHtml)
    
    process_template(el.getAttribute("mix-"+method))
}

// Add sanitization function
function sanitizeHtml(dirty) {
    // Create a new DOMParser
    const parser = new DOMParser()
    const doc = parser.parseFromString(dirty, 'text/html')
    
    // Remove potentially dangerous elements and attributes
    const dangerous = ['script', 'style', 'iframe', 'object', 'embed']  // Removed 'form' since you need it
    dangerous.forEach(tag => {
        doc.querySelectorAll(tag).forEach(node => node.remove())
    })
    
    // Remove dangerous attributes from remaining elements
    const dangerousAttrs = ['onerror', 'onload', 'onmouseover', 'onclick', 'onmouseout', 'onkeydown', 'onkeyup']
    doc.querySelectorAll('*').forEach(el => {
        dangerousAttrs.forEach(attr => el.removeAttribute(attr))
        
        // Remove javascript: and data: URLs
        if(el.href && (el.href.toLowerCase().startsWith('javascript:') || el.href.toLowerCase().startsWith('data:'))) {
            el.remove()
        }
        if(el.src && (el.src.toLowerCase().startsWith('javascript:') || el.src.toLowerCase().startsWith('data:'))) {
            el.remove()
        }
    })
    
    // Get both body content and any template tags that might be siblings
    const templates = Array.from(doc.querySelectorAll('template')).map(t => t.outerHTML).join('')
    const bodyContent = doc.body.innerHTML
    
    return templates + bodyContent
}

// ##############################
function process_template(mix_url){
    cl(`process_template() mix-url ${mix_url}`) 

    let new_url = false 
    
    if( document.querySelector("template[mix-redirect]") ){ 
        cl(`mix-redirect found`)
        location.href= document.querySelector("template[mix-redirect]").getAttribute("mix-redirect")
        return 
    }


    
    if( ! document.querySelector("template[mix-target]") && ! document.querySelector("template[mix-function]") ){ 
        cl(`eror = mix-target nor mix-function found`)
        return 
    }
    document.querySelectorAll('template[mix-target]').forEach(template => {
        // console.log("template", template)  

        if( template.getAttribute("mix-newurl") && new_url == false ){
            new_url = template.getAttribute("mix-newurl")
        }
        // cl(`new_url: ${new_url}`)

        if( ! template.getAttribute("mix-target") ){console.log(`process_template() - error - mix-target missing`); return}    
        console.log(`ok : mix() the response data will affect '${template.getAttribute("mix-target")}'`)
        if(! document.querySelector(template.getAttribute("mix-target")) ){console.log(`process_template() - error - mix-target is not in the dom`); return}   


        let position = "innerHTML"
        if( template.hasAttribute('mix-before')){position = "beforebegin"}
        if( template.hasAttribute("mix-after")){position = "afterend"}
        if( template.hasAttribute("mix-top")){position = "afterbegin"}
        if( template.hasAttribute("mix-bottom")){position = "beforeend"}
        if( template.hasAttribute("mix-replace")){position = "replace"}
        if(position == "innerHTML"){            
            document.querySelector(template.getAttribute("mix-target")).innerHTML = template.innerHTML
        }
        else if(position == "replace"){
            document.querySelector(template.getAttribute("mix-target")).insertAdjacentHTML("afterend", template.innerHTML)
            document.querySelector(template.getAttribute("mix-target")).remove()            
        }
        else{
            document.querySelector(template.getAttribute("mix-target")).insertAdjacentHTML(position, template.innerHTML)
        }        


        if( ! template.getAttribute("mix-push-url") ){ cl(`process_template() - optional - mix-push-url not set`) }
        template.remove()
        mix_convert();
        // Process newly injected elements and push to history
        mixonurl(mix_url)

    })
    document.querySelectorAll('template[mix-function]').forEach(template => {
        function_name = template.getAttribute("mix-function")
        console.log(`ok : mix() the response data will run the function '${function_name}'`)
        window[function_name](template.innerHTML)
        template.remove()
    })    
}


// ##############################
function mixonurl(mix_url, push_to_history = true){
    // cl(`mixonurl(xurl): ${mix_url}`)
    
    document.querySelectorAll(`[mix-on-url='${mix_url}']`).forEach( el => {
        // cl(el)
        const title = el.getAttribute("mix-title") || false
        // console.log(`ok : x() the xTitle is '${title}'`)
        if(title){ document.title = title}   

        if(el.getAttribute("mix-push-url") && push_to_history){
            cl("Pushing to history")
            // cl(el.dataset.xpushurl)
            history.pushState({"mixonurl":el.getAttribute("mix-push-url")}, "", el.getAttribute("mix-push-url"))
            // history.replaceState({"xonurl":el.dataset.xseturl}, "title", el.dataset.xseturl)
        }

        if(el.getAttribute("mix-hide")){
            // document.querySelector(el.dataset.xhide).classList.add("hidden")        
            document.querySelectorAll(el.getAttribute("mix-hide")).forEach( i => {
                // cl(`hidding element: ${el.getAttribute("mix-hide")}`) 
                // cl(i)               
                i.classList.add("hidden")
            })
        }
        if(el.getAttribute("mix-show")){
            document.querySelectorAll(el.getAttribute("mix-show")).forEach( i => {
                i.classList.remove("hidden")
            })
        }            
    })
}


// ##############################
window.onpopstate = function(event){
    cl(`##### onpopstate`)
    cl(event.state.mixonurl)
    mixonurl(event.state.mixonurl, false)
}


// ##############################
setInterval(function(){
    document.querySelectorAll("[mix-ttl]").forEach(el=>{
        if(el.getAttribute("mix-ttl") <= 0){
            el.remove()
        }else{
            el.setAttribute("mix-ttl", el.getAttribute("mix-ttl") - 1000)
        }
    })
}, 500)

// ##############################
function mix_convert(){
    document.querySelectorAll("[mix-get], [mix-delete], [mix-put], [mix-post]").forEach( el => {
        let method = "mix-get"
        if(el.hasAttribute("mix-delete")){ method = "mix-delete" }
        
        let url = ""
        if(el.getAttribute(method) == ""){    
            if( el.getAttribute("href")){
                el.setAttribute(`${method}`, el.getAttribute("href"))
            }
            if( el.getAttribute("action")){
                el.setAttribute(`${method}`, el.getAttribute("action"))
            }                            
        }
        if(!el.hasAttribute("mix-focus") && !el.hasAttribute("mix-blur")){
            // Replace onclick attribute with addEventListener
            el.addEventListener('click', (e) => {
                e.preventDefault()
                mixhtml(el)
            })
        }
    })  

    document.querySelectorAll("[mix-focus], [mix-blur]").forEach( el => {
        let eventType = 'click'
        if(el.hasAttribute("mix-focus")){ eventType = "focus" }
        if(el.hasAttribute("mix-blur")){ eventType = "blur" }
        
        // Replace on* attributes with addEventListener
        el.addEventListener(eventType, (e) => {
            e.preventDefault()
            mixhtml(el)
        })
    })     
}


mix_convert();