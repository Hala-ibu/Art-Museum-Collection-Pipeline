from io_utils import read_json, setup_logging, read_text


if __name__ == "__main__":
   setup_logging("pipeline.log")
   art_data1 = read_json("data/raw/artworks/Art_Institute_of_Chicago/artwork1.json")
   art_data2 = read_json("data/raw/artworks/Art_Institute_of_Chicago/artwork1.json")
   if art_data1:
       print("artwork title:", art_data1["title"])
    if art_data2:
       print("artwork title:", art_data2["title"])

