version ?= 17

clean:
	rm -rf target

install:
	pip install -r requirements.txt

build:
#	podman build --platform linux/amd64 . -f Containerfile.chroma -t llm_agent_finance_chroma:latest
	podman build --platform linux/amd64 . -f Containerfile.streamlit -t llm_agent_finance_streamlit:latest

push:
#	podman tag llm_agent_finance_chroma:latest quay.io/glroland/llm_agent_finance_chroma:$(version)
#	podman push quay.io/glroland/llm_agent_finance_chroma:$(version) --tls-verify=false
	podman tag llm_agent_finance_streamlit:latest quay.io/glroland/llm_agent_finance_streamlit:$(version)
	podman push quay.io/glroland/llm_agent_finance_streamlit:$(version) --tls-verify=false

stress: clean
	mkdir -p target/jmeter_report
	jmeter -n -t deploy/jmeter_stress_tests.jmx -l target/jmeter_results.log -e -o target/jmeter_report

chat:
	streamlit run app.py --server.port=8501 --server.address=0.0.0.0
