import React from "react";
import SearchForm from "./search";
function Home(){

    return (
        <div>
            <div >
        </div>
        <div>
            <div className="flex justify-around">
                <div className="w-1/3  mt-9">
                    <h2 className="text-[#53CEFF] text-5xl ">WHY US</h2>
                    <p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</p>
                </div>
                <SearchForm/>
            </div>
        </div>
        </div>
        
    )
}
export default Home