import pandas as pd

df = pd.read_csv("new/books_full.csv")

print("Tổng số dòng:", len(df))
print("Các cột:", list(df.columns))
print()

missing = df.isnull().sum()
print("Số ô bị thiếu theo cột:")
print(missing[missing > 0])
print()

empty_title_author = df[(df['title'].astype(str).str.strip() == "") | (df['author'].astype(str).str.strip() == "")]
print("Số dòng có 'title' hoặc 'author' bị trống:", empty_title_author.shape[0])
print()

only_title_rows = df[
    (df['title'].astype(str).str.strip() != "") &
    df[['author', 'description', 'thumbnail', 'publisher', 'publishing_year',
        'num_pages', 'language', 'categories', 'link']].isnull().all(axis=1)
]
print("Số dòng chỉ có 'title', còn lại trống toàn bộ:", only_title_rows.shape[0])
print()

mostly_empty_rows = df[df.isnull().sum(axis=1) >= 9]
print("Số dòng bị thiếu gần hết thông tin (>= 9 trường):", mostly_empty_rows.shape[0])
print()

duplicates = df.duplicated(subset=["title", "author"], keep=False)
print("Số dòng bị trùng tiêu đề + tác giả:", duplicates.sum())
print()

df["publishing_year"] = pd.to_numeric(df["publishing_year"], errors="coerce")
invalid_years = df[(df["publishing_year"] < 1900) | (df["publishing_year"] > 2025)]
print("Số dòng có năm xuất bản bất thường (<1900 hoặc >2025):", invalid_years.shape[0])
print()

df["num_pages"] = pd.to_numeric(df["num_pages"], errors="coerce")
print("Trung bình số trang:", df['num_pages'].mean(skipna=True))
print("Số dòng có số trang = 0:", df[df['num_pages'] == 0].shape[0])
print()

print("Ngôn ngữ phổ biến:")
print(df["language"].value_counts(dropna=True).head(5))
print()

print("Top 10 thể loại:")
print(df["categories"].value_counts(dropna=True).head(10))
