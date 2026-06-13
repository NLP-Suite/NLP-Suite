# Use amazon corretto as base image, it's an open-jdk.
FROM amazoncorretto:17

# Install unzip, curl, and Python
RUN yum install -y unzip curl python3 

#Install fastapi and uvicorn.
RUN pip3 install fastapi uvicorn

# Install MALLET
RUN curl -LO http://mallet.cs.umass.edu/dist/mallet-2.0.8.zip && \
    unzip mallet-2.0.8.zip && \
    mv mallet-2.0.8 /opt/mallet

# Set MALLET environment variables
ENV MALLET_HOME=/opt/mallet
ENV PATH="${MALLET_HOME}/bin:${PATH}"
ENV CLASSPATH="${MALLET_HOME}/class"

# Link mallet script (optional now, but can keep, makes it easier to run commands)
RUN ln -s /opt/mallet/bin/mallet /usr/local/bin/mallet

# Add the FastAPI app and input file (safe location -> optional folder?)
COPY api.py /opt/mallet_api/api.py

WORKDIR /opt/mallet_api

EXPOSE 5050

#RUN FastAPI with uvicorn 
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5050"]

