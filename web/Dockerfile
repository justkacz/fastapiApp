# 
FROM python:3.9-slim

# prevents from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# 
WORKDIR /fastapiapp

# 
# COPY ../requirements.txt /app/fastapiapp/requirements.txt
COPY ../requirements.txt ./requirements.txt


# 
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# 
# COPY . ./fastapiapp
COPY . .

# 
CMD ["fastapi", "run", "web/main.py", "--port", "8000"]