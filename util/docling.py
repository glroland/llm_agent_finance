import glob
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.ocr_mac_model import OcrMacOptions


class PDFConverter:
    def __init__(self, mode="default"):
        """
        Initialize the PDFConverter with the selected mode.

        Args:
            mode (str): "default" for standard conversion, "mac_ocr" for OCR-based conversion.
        """
        self.mode = mode
        self.doc_converter = self._initialize_converter()

    def _initialize_converter(self):
        """Set up the appropriate DocumentConverter based on the mode."""
        if self.mode == "mac_ocr":
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.do_cell_matching = True
            pipeline_options.ocr_options = OcrMacOptions()

            return DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        elif self.mode == "ocr":
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.ocr_options.use_gpu = False  # <-- set this.
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.do_cell_matching = True

            return DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        else:
            return DocumentConverter()

    def convert_pdf(self, input_dir: str, output_dir: str) -> None:
        """
        Convert all PDFs in the input directory to Markdown and save them to the output directory.

        Args:
            input_dir (str): Directory containing PDF files.
            output_dir (str): Directory for converted Markdown files.
        """
        input_pdfs = glob.glob(f"{input_dir}/*.pdf")

        if not input_pdfs:
            print(f"No PDFs found in {input_dir}.")
            return

        for i in input_pdfs:
            conv_result = self.doc_converter.convert(i)
            with open(f"{output_dir}/{conv_result.input.file.stem}.md", "w") as f:
                f.write(conv_result.document.export_to_markdown())
