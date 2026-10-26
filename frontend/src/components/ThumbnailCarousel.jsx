import { useRef } from "react";
import { Splide, SplideSlide } from "@splidejs/react-splide";
import "@splidejs/react-splide/css";

export default function ThumbnailCarousel({ imageURLs, onImageClick }) {
    if (imageURLs.length === 0) {
        return
    }

    const mainOptions = {
        perPage: 1,
        perMove: 1,
        gap: "1rem",
        pagination: false,
    };

    const style = {
        width: "100%",
        height: "auto",
        borderRadius: "10px",
        justifySelf: "center"
    };

    const btn_img = {
        width: "4em",
        height: "4em",
        overflow: "hidden",
        listStyle: "none",
        cursor: "pointer"
    }

    const mainRef = useRef(null);

    const handleThumbs = (id) => {
        if (mainRef.current) {
        mainRef.current.go(id);
        }
    };

    if (imageURLs.length === 1) {
        return (
            <div className="thumbnail-carousel">
                <button
                    type="button"
                    className="thumbnail-carousel__image"
                    onClick={() => onImageClick(imageURLs[0])}
                    aria-label="View item image full size"
                >
                    <img src={imageURLs[0]} alt="Item" style={style} />
                </button>
            </div>
        );
    }

    return (
        <div className="thumbnail-carousel">
            <Splide options={mainOptions} ref={mainRef} style={{}}>
                {imageURLs.map((imageURL, index) =>
                    <SplideSlide key={`${imageURL}-${index}`}>
                        <button
                            type="button"
                            className="thumbnail-carousel__image"
                            onClick={() => onImageClick(imageURL)}
                            aria-label="View item image full size"
                        >
                            <img src={imageURL} alt="Item" style={style} />
                        </button>
                    </SplideSlide>
                )}
            </Splide>

            <ul className="thumbnail-carousel__buttons">
                {imageURLs?.map((thumbnail, index) => (
                <li key={thumbnail}>
                    <button type="button" onClick={() => handleThumbs(index)}>
                    <img
                        src={thumbnail}
                        alt="product thumbnail"
                        style={btn_img}
                    />
                    </button>
                </li>
                ))}
            </ul>
        </div>
    );
    }
        
