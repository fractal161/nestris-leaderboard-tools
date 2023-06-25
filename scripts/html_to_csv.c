#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <zconf.h>
#include <zlib.h>
#include <libxml/HTMLparser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

#define CHUNK 100000

static int read_chunk(gzFile *data, char *buf, int size) {
    int bytes_read = gzread(*data, buf, size);
    if (bytes_read < size) {
        buf[bytes_read] = '\0';
    }
    return bytes_read;
}

// https://gnome.pages.gitlab.gnome.org/libxml2/tutorial/apd.html
xmlXPathObjectPtr get_node_set(xmlDocPtr doc, xmlChar *xpath, xmlNodePtr node) {
    xmlXPathContextPtr context;
    xmlXPathObjectPtr result;

    context = xmlXPathNewContext(doc);
    if (context == NULL) {
        printf("Error in xmlXPathNewContext\n");
        return NULL;
    }
    if (node != NULL) {
        context->node = node;
    }
    result = xmlXPathEvalExpression(xpath, context);
    xmlXPathFreeContext(context);
    if (result == NULL) {
        printf("Error in xmlXPathEvalExpression\n");
        return NULL;
    }
    if(xmlXPathNodeSetIsEmpty(result->nodesetval)){
        xmlXPathFreeObject(result);
        return NULL;
    }
    return result;
}

// https://qnaplus.com/print-xml-file-tree-form-libxml2-c-programming/
static int is_leaf(xmlNode * node) {
    xmlNode * child = node->children;
    while(child) {
        if(child->type == XML_ELEMENT_NODE) return 0;
        child = child->next;
    }
    return 1;
}

static void print_xml(xmlNode * node, int indent_len) {
    while(node)
    {
        if(node->type == XML_ELEMENT_NODE)
        {
            printf(
                "%*c%s:%s\n",
                indent_len*2,
                '-', 
                node->name, 
                is_leaf(node) ? xmlNodeGetContent(node) :
                    xmlGetProp(node, (xmlChar*) "id")
            );
        }
        print_xml(node->children, indent_len + 1);
        node = node->next;
    }
}

static void print_element_names(xmlNode * a_node) {
    xmlNode *cur_node = NULL;

    for (cur_node = a_node; cur_node; cur_node = cur_node->next) {
        if (cur_node->type == XML_ELEMENT_NODE) {
            printf("node type: Element, name: %s\n", cur_node->name);
        }

        print_element_names(cur_node->children);
    }
}

static void escape_csv_entry(xmlChar *entry) {

}

static inline void write_csv_entry(xmlDocPtr doc, xmlNodePtr td, FILE* file) {
    xmlChar *entry;
    //xmlChar *a_xpath = (xmlChar*) "./a";
    entry = xmlNodeGetContent(td);
    // if td_string contains a comma, double quote, or newline/carriage return,
    // surround string in double quotes
    // furthermore, each double quote must be itself doubled
    // if td contains a url, use that instead of the text
    fputs((char*) entry, file);
    xmlChar *rowspan = xmlGetProp(td, (xmlChar*) "rowspan");
    if (rowspan) {
        int span = atoi((char*) rowspan);
        for (int i = 0; i < span - 1; i++) {
            fputs(",", file);
            fputs((char*) entry, file);
        }
        xmlFree(rowspan);
    }
    xmlFree(entry);
}

static void write_csv_row(xmlDocPtr doc, xmlNodePtr tr, FILE* file) {
    xmlXPathObjectPtr td_xpath_obj = get_node_set(doc, (xmlChar*) "./td", tr);
    if (td_xpath_obj) {
        xmlNodeSetPtr td_nodes = td_xpath_obj->nodesetval;
        for (int i = 0; i < td_nodes->nodeNr; i++) {
            xmlNodePtr td = td_nodes->nodeTab[i];
            write_csv_entry(doc, td, file);
            if (i < td_nodes->nodeNr - 1) {
                fputs(",", file);
            }
        }
        fputs("\n", file);
        xmlXPathFreeObject(td_xpath_obj);
    }
}

static void write_table_to_csv(xmlDocPtr doc, xmlNodePtr table, FILE* file) {
    xmlXPathObjectPtr tr_xpath_obj = get_node_set(doc, (xmlChar*) "./tbody/tr", table);
    if (tr_xpath_obj) {
        xmlNodeSetPtr tr_nodes = tr_xpath_obj->nodesetval;
        for (int i = 0; i < tr_nodes->nodeNr; i++) {
            xmlNodePtr tr = tr_nodes->nodeTab[i];
            write_csv_row(doc, tr, file);
        }
        xmlXPathFreeObject(tr_xpath_obj);
    }
}

// basically taken from http://www.xmlsoft.org/examples/parse4.c
int main(int argc, char* argv[]) {
    for (int i = 30000; i < 31000; i++) {
        printf("parsing revision %d\n", i);
        char in_file[100];
        sprintf(in_file, "../data/raws/1078039113/%d.html.gz", i);
        gzFile data_file = gzopen(in_file, "r");
        char buf[CHUNK+1];

        // set up parser
        int bytes_read = read_chunk(&data_file, buf, CHUNK);
        htmlParserCtxtPtr ctxt = htmlCreatePushParserCtxt(NULL, NULL, buf,
            CHUNK, NULL, XML_CHAR_ENCODING_UTF8);
        if (ctxt == NULL) {
            fprintf(stderr, "Failed to create parser context !\n");
            return 1;
        }
        htmlDocPtr doc;

        // process all chunks
        while (!gzeof(data_file)) {
            bytes_read = read_chunk(&data_file, buf, CHUNK);
            htmlParseChunk(ctxt, buf, bytes_read, 0);
        }
        int last_parse = htmlParseChunk(ctxt, buf, 0, 1);

        // finish setup of document
        doc = ctxt->myDoc;
        xmlNode *root_element = xmlDocGetRootElement(doc);

        int res = ctxt->wellFormed;
        htmlFreeParserCtxt(ctxt);
        if (!res) {
            fprintf(stderr, "Failed to parse %s\n", in_file);
            return 1;
        }
        gzclose_r(data_file);

        xmlXPathObjectPtr tr_xpath_obj = get_node_set(doc, (xmlChar*) "//table/tbody/tr", NULL);
        if (tr_xpath_obj) {
            xmlNodeSetPtr tr_nodes = tr_xpath_obj->nodesetval;
            char out_file_name[100];
            sprintf(out_file_name, "../data/revs/1078039113/%d.csv", i);
            FILE *out_file = fopen(out_file_name, "wb");

            for (int j = 0; j < tr_nodes->nodeNr; j++) {
                htmlNodePtr tr = tr_nodes->nodeTab[j];
                write_csv_row(doc, tr, out_file);
            }
            fclose(out_file);
            xmlXPathFreeObject(tr_xpath_obj);
        }
        else {
            fprintf(stderr, "Table not found\n");
            return 1;
        }
        
        // clean up memory
        xmlFreeDoc(doc);
        xmlCleanupParser();
    }
}
